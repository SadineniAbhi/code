import subprocess
from pathlib import Path
from string import Template
from google.api_core.exceptions import GoogleAPICallError
from google.cloud.devtools import cloudbuild_v1
from fastmcp import FastMCP

mcp = FastMCP("kubernetes mcp server")

ARTIFACT_REGISTRY = "us-central1-docker.pkg.dev/stocket-prod/finalproj"
PROJECT_ID = "stocket-prod"


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

    trigger = cloudbuild_v1.BuildTrigger(
        name=trigger_name,
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
        service_account=f"projects/{PROJECT_ID}/serviceAccounts/test-643@stocket-prod.iam.gserviceaccount.com",
    )

    existing = None
    try:
        async for t in await client.list_build_triggers(project_id=PROJECT_ID):
            if t.name == trigger_name:
                existing = t
                break
    except GoogleAPICallError as e:
        return f"Failed to list Cloud Build triggers: {e}"

    if existing:
        trigger.id = existing.id
        try:
            updated = await client.update_build_trigger(
                project_id=PROJECT_ID, trigger_id=existing.id, trigger=trigger
            )
            trigger_id = updated.id
        except GoogleAPICallError as e:
            return f"Failed to update trigger '{trigger_name}': {e}"
    else:
        try:
            created = await client.create_build_trigger(
                project_id=PROJECT_ID, trigger=trigger
            )
            trigger_id = created.id
        except GoogleAPICallError as e:
            return f"Failed to create trigger '{trigger_name}': {e}"

    try:
        operation = await client.run_build_trigger(
            project_id=PROJECT_ID,
            trigger_id=trigger_id,
            source=cloudbuild_v1.RepoSource(branch_name=branch),
        )
        run_response = await operation.result()
    except GoogleAPICallError as e:
        return f"Trigger '{trigger_name}' created but failed to run build: {e}"

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
    mcp.run("streamable-http", port=5000)
