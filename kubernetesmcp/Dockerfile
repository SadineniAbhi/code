FROM registry.k8s.io/kubectl:v1.31.4 AS kubectl
FROM ghcr.io/astral-sh/uv:0.8.15 AS uv

FROM python:3.13-slim

COPY --from=uv /uv /uvx /bin/
COPY --from=kubectl /bin/kubectl /usr/local/bin/kubectl

WORKDIR /app

# Create the venv against the base image's own Python *before* installing
# any apt packages below. apt pulls in a separate Debian python3 as a
# transitive dependency of curl/gnupg, and purging/autoremoving them
# afterwards removes that package again — if uv had bound the venv to it
# instead of the image's /usr/local Python, the venv's interpreter symlink
# ends up dangling.
COPY pyproject.toml uv.lock README.md ./
# --python pins the interpreter explicitly: uv's auto-discovery in this
# image resolves to a phantom /usr/bin/python3.13 that doesn't exist,
# leaving the venv's python symlink dangling (ModuleNotFoundError at
# runtime despite packages installing without error at build time).
RUN uv sync --frozen --no-dev --no-install-project --python /usr/local/bin/python3.13 \
    && rm -f .venv/bin/python .venv/bin/python3 .venv/bin/python3.13 \
    && ln -s /usr/local/bin/python3.13 .venv/bin/python \
    && ln -s python .venv/bin/python3 \
    && ln -s python .venv/bin/python3.13 \
    && .venv/bin/python -c "import google; print('venv python OK:', google.__file__)"

# gke-gcloud-auth-plugin: required by kubectl to authenticate against GKE
# clusters via the mounted kubeconfig's exec-credential plugin.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg ca-certificates \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
        > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        google-cloud-cli google-cloud-cli-gke-gcloud-auth-plugin \
    && apt-get purge -y curl gnupg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV USE_GKE_GCLOUD_AUTH_PLUGIN=True

COPY . .
RUN chmod +x entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 5000
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "main.py"]
