import asyncio
import os
import subprocess
from pathlib import Path
from string import Template
from google.api_core.exceptions import GoogleAPICallError
from google.cloud.devtools import cloudbuild_v1
from fastmcp import FastMCP

mcp = FastMCP("kubernetes mcp server")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "project-2026-486210")
ARTIFACT_REGISTRY_REPO = os.environ.get("ARTIFACT_REGISTRY_REPO", "coding-agent-project")
ARTIFACT_REGISTRY_REGION = os.environ.get("ARTIFACT_REGISTRY_REGION", "us-central1")
ARTIFACT_REGISTRY = f"{ARTIFACT_REGISTRY_REGION}-docker.pkg.dev/{PROJECT_ID}/{ARTIFACT_REGISTRY_REPO}"

# Cloud Build triggers live in a specific region, not "global" — it must match
# the region the GitHub App connection was authorized in (see the "Connect
# repository" flow in the console). A trigger created in the wrong location
# is invisible to (and can't be created alongside) that connection.
CLOUDBUILD_REGION = os.environ.get("CLOUDBUILD_REGION", "us-central1")

# Cloud Build now requires triggers to run as an explicit, permissioned
# service account rather than falling back to a legacy default.
CLOUDBUILD_SERVICE_ACCOUNT = os.environ.get(
    "CLOUDBUILD_SERVICE_ACCOUNT",
    f"projects/{PROJECT_ID}/serviceAccounts/devops-agent-sa@{PROJECT_ID}.iam.gserviceaccount.com",
)


async def create_gcp_trigger(
    github_repo: str,
    dockerfile_path: str,
    trigger_name: str,
    branch: str,
    image_name: str,
) -> str:
    """Create a GCP Cloud Build trigger for a GitHub repo and run it.

    Args:
        github_repo: GitHub repo in "owner/repo" format.
        dockerfile_path: Path to the Dockerfile within the repo (e.g. "Dockerfile" or "services/api/Dockerfile").
        trigger_name: Name for the Cloud Build trigger.
        branch: Branch name to trigger on and run against (e.g. "main").
        image_name: Image name to push to Artifact Registry (e.g. "my-app").
    """
    if "/" not in github_repo:
        return f"Invalid github_repo format '{github_repo}': expected 'owner/repo'"
    owner, repo = github_repo.split("/", 1)
    image_uri = f"{ARTIFACT_REGISTRY}/{image_name}:latest"

    client = cloudbuild_v1.CloudBuildAsyncClient()
    parent = f"projects/{PROJECT_ID}/locations/{CLOUDBUILD_REGION}"

    trigger = cloudbuild_v1.BuildTrigger(
        name=trigger_name,
        service_account=CLOUDBUILD_SERVICE_ACCOUNT,
        github=cloudbuild_v1.GitHubEventsConfig(
            owner=owner,
            name=repo,
            push=cloudbuild_v1.PushFilter(branch=f"^{branch}$"),
        ),
        build=cloudbuild_v1.Build(
            steps=[
                cloudbuild_v1.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    args=["build", "-t", image_uri, "-f", dockerfile_path, "."],
                )
            ],
            images=[image_uri],
            options=cloudbuild_v1.BuildOptions(
                logging=cloudbuild_v1.BuildOptions.LoggingMode.CLOUD_LOGGING_ONLY,
            ),
        ),
    )

    existing = None
    try:
        list_request = cloudbuild_v1.ListBuildTriggersRequest(parent=parent)
        async for t in await client.list_build_triggers(request=list_request):
            if t.name == trigger_name:
                existing = t
                break
    except GoogleAPICallError as e:
        return f"Failed to list Cloud Build triggers: {e}"

    # The installed client's update_build_trigger only supports the legacy
    # global-location addressing (project_id + trigger_id), which 404s on a
    # regional trigger. Reconcile by delete-then-create instead, which does
    # support regional resource names.
    if existing:
        try:
            await client.delete_build_trigger(name=f"{parent}/triggers/{existing.id}")
        except GoogleAPICallError as e:
            return f"Failed to replace existing trigger '{trigger_name}': {e}"

    try:
        created = await client.create_build_trigger(parent=parent, trigger=trigger)
        trigger_id = created.id
    except GoogleAPICallError as e:
        return f"Failed to create trigger '{trigger_name}': {e}"

    # Note: we deliberately don't await operation.result() here. This
    # client's generic LRO polling addresses the operation by global
    # location and 404s for a regional trigger/build, even though the build
    # itself runs fine. Instead we read the build id straight off the
    # operation's metadata (available immediately) and poll get_build
    # ourselves, using proper regional addressing.
    try:
        run_request = cloudbuild_v1.RunBuildTriggerRequest(
            name=f"{parent}/triggers/{trigger_id}",
            source=cloudbuild_v1.RepoSource(branch_name=branch),
        )
        operation = await client.run_build_trigger(request=run_request)
        build_id = operation.metadata.build.id
    except GoogleAPICallError as e:
        return f"Trigger '{trigger_name}' created but failed to start build: {e}"

    terminal_statuses = {
        cloudbuild_v1.Build.Status.SUCCESS,
        cloudbuild_v1.Build.Status.FAILURE,
        cloudbuild_v1.Build.Status.INTERNAL_ERROR,
        cloudbuild_v1.Build.Status.TIMEOUT,
        cloudbuild_v1.Build.Status.CANCELLED,
        cloudbuild_v1.Build.Status.EXPIRED,
    }
    build_name = f"{parent}/builds/{build_id}"
    try:
        for _ in range(120):  # up to ~20 minutes
            run_response = await client.get_build(name=build_name)
            if run_response.status in terminal_statuses:
                break
            await asyncio.sleep(10)
        else:
            return (
                f"Trigger '{trigger_name}' started build {build_id} but it did not "
                f"finish within the wait budget. Check {run_response.log_url}"
            )
    except GoogleAPICallError as e:
        return f"Trigger '{trigger_name}' started build {build_id} but polling its status failed: {e}"

    if run_response.status != cloudbuild_v1.Build.Status.SUCCESS:
        return (
            f"Build {build_id} for trigger '{trigger_name}' finished with status "
            f"{run_response.status.name}. Check {run_response.log_url}"
        )

    return f"Successfully ran GCP Cloud Build trigger '{trigger_name}' for {github_repo} on branch '{branch}'. Build ID: {run_response.id}. Image: {image_uri}"


@mcp.tool()
async def deploy(
    github_repo: str,
    dockerfile_path: str,
    trigger_name: str,
    branch: str,
    image_name: str,
    port: int,
    deployment_name: str,
) -> str:
    res = await create_gcp_trigger(
        github_repo, dockerfile_path, trigger_name, branch, image_name
    )
    # Cloud Build reports the build SUCCESS before the pushed image is
    # always fully readable from Artifact Registry — pulling immediately
    # can 404 on the very first attempt. Give it a moment to propagate.
    await asyncio.sleep(20)
    try:
        deployment, service = get_k8s_manifests(image_name, port, deployment_name)
    except FileNotFoundError as e:
        return f"{res}\n\nFailed to load k8s manifest templates: {e}"
    except ValueError as e:
        return f"{res}\n\nFailed to render k8s manifests: {e}"
    try:
        kubectl_apply(deployment)
        kubectl_apply(service)
    except FileNotFoundError:
        return f"{res}\n\nFailed to apply k8s manifests: kubectl not found — is it installed and on PATH?"
    except RuntimeError as e:
        return f"{res}\n\nFailed to apply k8s manifests: {e}"
    return res


STATIC_DIR = Path(__file__).parent / "static"


def get_k8s_manifests(
    image_name: str, port: int, deployment_name: str
) -> tuple[str, str]:
    image_uri = f"{ARTIFACT_REGISTRY}/{image_name}:latest"
    values = {"PORT": port, "IMAGE": image_uri, "NAME": deployment_name}

    deployment = Template((STATIC_DIR / "deployment.yaml").read_text()).substitute(
        values
    )
    service = Template((STATIC_DIR / "service.yaml").read_text()).substitute(values)

    return deployment, service


def kubectl_apply(manifest: str) -> str:
    result = subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=manifest,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


if __name__ == "__main__":
    # Bind to all interfaces so the Agent container can reach this service.
    mcp.run("streamable-http", host="0.0.0.0", port=5000)
