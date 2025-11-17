FROM ghcr.io/home-assistant/devcontainer:supervisor

# Install utilities needed for HACS installation and development
USER root
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    unzip \
    python3-venv \
    python3-pip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Ensure /workspaces exists (the base image should provide it) and set workdir
WORKDIR /workspaces/ha_backup_octopus

# Create a non-root user if image doesn't provide one (the base image may already)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN if ! id -u $USERNAME >/dev/null 2>&1; then \
      groupadd -g $USER_GID $USERNAME || true; \
      useradd -m -s /bin/bash -u $USER_UID -g $USER_GID $USERNAME || true; \
    fi

USER $USERNAME
