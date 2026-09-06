FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Control Codespace image. *-org repos must set
#   "image": "ghcr.io/e-st/bellen:<VERSION>"
# with no features and no onCreateCommand. Do not install gh/node/grok/canvas at start.

ENV DEBIAN_FRONTEND=noninteractive \
    GROK_BIN_DIR=/usr/local/bin \
    UV_INSTALL_DIR=/usr/local/bin \
    UV_CACHE_DIR=/home/vscode/.cache/uv \
    npm_config_update_notifier=false \
    PATH="/usr/local/bin:${PATH}"

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg tmux openssl git \
 && mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
 && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
 && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
      | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
      > /etc/apt/sources.list.d/nodesource.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends gh nodejs \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && ln -sf /usr/local/bin/uv /usr/bin/uv \
 && ln -sf /usr/local/bin/uvx /usr/bin/uvx \
 && uv --version && uvx --version

RUN curl -fsSL https://x.ai/cli/install.sh | bash \
 && command -v grok \
 && [ -e /usr/bin/grok ] || ln -sf /usr/local/bin/grok /usr/bin/grok

COPY package.json /opt/bellen/package.json
COPY warm-uvx.js /opt/bellen/warm-uvx.js
RUN npm install -g "@openhands/agent-canvas@$(node -p "require('/opt/bellen/package.json').dependencies['@openhands/agent-canvas']")" \
 && npm cache clean --force \
 && command -v agent-canvas \
 && agent-canvas --version

RUN GROK_REAL=$(readlink -f /usr/local/bin/grok) \
 && install -m 0755 "$GROK_REAL" /usr/local/lib/grok \
 && ln -sfn /usr/local/lib/grok /usr/local/bin/grok \
 && ln -sfn /usr/local/lib/grok /usr/local/bin/agent \
 && ln -sfn /usr/local/lib/grok /usr/bin/grok \
 && ln -sfn /usr/local/lib/grok /usr/bin/agent \
 && chmod a+rx /usr/local/bin/uv /usr/local/bin/uvx /usr/bin/agent-canvas \
 && mkdir -p /home/vscode/.cache/uv /home/vscode/.local/bin \
 && echo 'export PATH="/usr/local/bin:/usr/bin:$HOME/.local/bin:$PATH"' >> /home/vscode/.bashrc \
 && echo 'export UV_CACHE_DIR="${UV_CACHE_DIR:-$HOME/.cache/uv}"' >> /home/vscode/.bashrc \
 && chown -R vscode:vscode /home/vscode/.cache /home/vscode/.local /home/vscode/.bashrc

USER vscode
WORKDIR /workspaces
ENV HOME=/home/vscode \
    UV_CACHE_DIR=/home/vscode/.cache/uv \
    PATH="/usr/local/bin:/home/vscode/.local/bin:${PATH}"

RUN node /opt/bellen/warm-uvx.js

RUN for b in gh node npm uv uvx grok agent-canvas tmux git; do \
      command -v "$b" || { echo "missing $b"; ls -l /usr/local/bin /usr/bin | head; exit 1; }; \
    done
