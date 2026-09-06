#!/usr/bin/env bash
export PATH="/usr/local/bin:$HOME/.local/bin:$PATH"
export TMUX_TMPDIR="${TMUX_TMPDIR:-/tmp}"
mkdir -p "${PLATFORM:-/workspaces/platform}" "$HOME/.openhands"

if [ -z "$LOCAL_BACKEND_API_KEY" ]; then
  LOCAL_BACKEND_API_KEY=$(openssl rand -base64 32)
  export LOCAL_BACKEND_API_KEY
  umask 077
  printf '%s\n' "$LOCAL_BACKEND_API_KEY" > "$HOME/.openhands/local-backend-api-key"
  echo "LOCAL_BACKEND_API_KEY was unset; generated $HOME/.openhands/local-backend-api-key (paste that in the Canvas UI)."
fi

if ! curl -sf -o /dev/null --max-time 2 http://127.0.0.1:8000/; then
  nohup agent-canvas --public --port 8000 >> "$HOME/.openhands/agent-canvas.log" 2>&1 &
  echo $! > "$HOME/.openhands/agent-canvas.pid"
  n=0
  while [ "$n" -lt 90 ]; do
    curl -sf -o /dev/null --max-time 2 http://127.0.0.1:8000/ && break
    n=$((n+1))
    sleep 1
  done
  if ! curl -sf -o /dev/null --max-time 2 http://127.0.0.1:8000/; then
    echo "Agent Canvas did not bind :8000. Last log:"
    tail -50 "$HOME/.openhands/agent-canvas.log"
  fi
fi

printf 'repos:\n' > "$PLATFORM/repos.yml"
(
  IFS=','
  for spec in $REPOS; do
    spec=$(printf '%s' "$spec" | sed 's/^ *//;s/ *$//')
    [ -z "$spec" ] && continue
    printf '  - %s\n' "$spec" >> "$PLATFORM/repos.yml"
    dest="$PLATFORM/${spec##*/}"
    [ -d "$dest/.git" ] || gh repo clone "$spec" "$dest" || echo "clone failed: $spec"
  done
) >> "$HOME/.openhands/clone.log" 2>&1 &
