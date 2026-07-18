ARG BUILD_FROM=ghcr.io/home-assistant/base:3.23
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    git \
    openssh-client \
    python3 \
    py3-requests \
    py3-yaml \
    rsync

COPY app /opt/gitops-sync
COPY rootfs /

RUN chmod 0755 /etc/services.d/gitops-sync/run \
    && python3 -m py_compile /opt/gitops-sync/main.py

LABEL \
    org.opencontainers.image.title="Home Assistant App: GitOps Sync" \
    org.opencontainers.image.description="Fail-safe bidirectional Git synchronization for Home Assistant configuration." \
    org.opencontainers.image.source="https://github.com/Togarriapa/HomeAssistant-Custom-Integrations" \
    org.opencontainers.image.licenses="MIT"
