# fspure-org

This is the thin control repo `e-St/fspure-org`.
Product code lives in separate repos. Git is the shared disk.

On Codespace start, product repos are cloned under `/workspaces/platform` from `containerEnv.REPOS`:

- `e-St/fspure`
- `e-St/fspure-ready-lib`
- `e-St/fstarter`

## Labels

- `agent` — unattended work via gh-aw on GitHub Actions. Never combine with `canvas`.
- `canvas` — interactive work in this control Codespace (Agent Canvas). Never combine with `agent`.

## Interactive (`canvas`)

1. Codespace on **this** repo (not a product repo).
2. Port 8000 only — Agent Canvas, visibility org. Image `ghcr.io/e-st/bellen`.
3. ACP: `grok agent stdio`
4. Workspace: `/workspaces/platform`

Do not prompt inside a product-repo editor. Humans inspect:

`https://codespaces.new/OWNER/PRODUCT?ref=agent/…`

## Unattended (`agent`)

Issues labeled `agent` on this repo run `.github/workflows/agent.md` after a human has run `gh aw compile`.
Push to the product remotes. Open PRs there.
