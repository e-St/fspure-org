# fspure-org

Thin **control** repo (`e-St/fspure-org`). Product code is not here.
Created from [bellen](https://github.com/e-St/bellen).

## Update from bellen

[https://github.com/e-St/fspure-org/actions/workflows/update-from-bellen.yml](https://github.com/e-St/fspure-org/actions/workflows/update-from-bellen.yml) → **Run workflow**. That opens a PR with the latest control image and files. Your product repo list is kept. Merge, then rebuild the Codespace.

## Codespace

1. Code → Create codespace on `main` (after merge). Image: `ghcr.io/e-st/bellen:1.1.0`.
2. Wait for start (Agent Canvas on port 8000, then product clones).
3. Ports → **8000** (`agent-canvas`, visibility org). Only this port is forwarded.
4. Paste `LOCAL_BACKEND_API_KEY` in the Canvas UI (Codespace secret, or `$HOME/.openhands/local-backend-api-key` if unset).
5. ACP command: `grok agent stdio`
6. Workspace: `/workspaces/platform`

Product repos cloned there:

- `e-St/fspure`
- `e-St/fspure-ready-lib`
- `e-St/fstarter`

## Labels

| Label | Meaning |
| --- | --- |
| `agent` | Unattended gh-aw on Actions. |
| `canvas` | Interactive Canvas in this Codespace. |

Never apply both to the same issue. File issues on this control repo.

## Inspect

Do not prompt in a product editor. Open the product repo's own Codespace:

`https://codespaces.new/OWNER/PRODUCT?ref=agent/…`
