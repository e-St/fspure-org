![bellen](docs/logo.jpg)

# bellen

Public starter for a **multi-repo** working model: a thin control repo (`*-org`) plus separate product repos. Git is the shared disk.

Use **OWNER/something-org** as the name of each new control repo (example of a real one: `e-St/fspure-org`). This repository is the template and the GitHub Pages form that bootstraps those control repos. It is not a product monorepo.

## 1. What this is

You keep product code in its own repos. You do **not** turn this template, or a control repo copied from it, into an app workspace.

| Piece | Role |
| --- | --- |
| **This repo (`e-St/bellen`)** | Template + Pages initializer (`docs/index.html`) + control image (`ghcr.io/e-st/bellen`) |
| **Control repo `OWNER/something-org`** | Thin GitHub Codespace: pulls `ghcr.io/e-st/bellen`, Agent Canvas on port 8000 |
| **Product repos** | Real apps/libraries. Each has its **own** `.devcontainer` / Codespace |
| **GitHub Actions (`gh-aw`)** | Unattended work when an issue is labeled `agent` |
| **Agent Canvas** | Interactive work in the **control** Codespace when labeled `canvas` |

Interactive sessions use Agent Canvas with ACP command `grok agent stdio`. Humans inspect agent branches in the **product** repo’s editor. Do not prompt in the product editor.

## 2. Architecture

```
                    ┌─────────────────────────────────────┐
  labeled `canvas`  │  Control Codespace                  │
  ─────────────────►│  OWNER/something-org                │
                    │  image: ghcr.io/e-st/bellen         │
                    │    (Canvas + Grok + gh, from this   │
                    │     repo’s image/ Dockerfile)       │
                    │  clones product repos →             │
                    │    /workspaces/platform             │
                    │  port 8000 only (org) = Agent Canvas│
                    │  ACP: grok agent stdio              │
                    └─────────────────────────────────────┘
                                      │
                                      │ git push / pull
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  Product repos (separate)           │
                    │  OWNER/something, OWNER/other, …    │
                    │  own .devcontainer / Codespaces     │
                    │  inspect: codespaces.new/…?ref=     │
                    └─────────────────────────────────────┘

  labeled `agent`  ──►  GitHub Actions on the control repo
                        (gh-aw, after a human ran `gh aw compile`)
```

- **Control Codespace** — one thin machine for the agent, running `ghcr.io/e-st/bellen`. Product toolchains do **not** belong here. Only port **8000** is forwarded.
- **Product Codespaces** — humans open these to inspect branches. Each product repo keeps its own devcontainer.
- **Actions** — unattended `agent` runs. No Canvas UI.

Never put both `agent` and `canvas` on the same issue.

## 3. One-time (maintainers of bellen)

Do this on **https://github.com/e-St/bellen** (cannot be set from files):

1. **Settings → General → Template repository** — check “Template repository”.
2. **Settings → Pages** — Deploy from branch **main**, folder **/docs**.
3. Confirm **https://e-st.github.io/bellen/** serves `docs/index.html`.
4. Workflow **Publish control image** pushes `ghcr.io/e-st/bellen:<image/VERSION>`. The package must be **public** so `*-org` Codespaces can pull it.

Copies of this template inherit `.github/workflows/after-mastart-pr.yml` and `.github/workflows/update-from-bellen.yml` (Actions → **Update from bellen**). They do not inherit GitHub Pages, the template flag, or GHCR; those stay on bellen.

## 4. Each new project

1. On GitHub: **Use this template** → create **`OWNER/something-org`** (empty README is fine; this template already has files).
2. Open **https://e-st.github.io/bellen/**. Type the control repo `OWNER/something-org` in the form. (`?repo=OWNER/something-org` is an optional shortcut that only prefills that box.)
3. Fill **product repos** (one `owner/name` per line).
4. Yes, **you** create the PAT on GitHub — bellen cannot mint one. As soon as the product repos parse, the page shows **Create the token on GitHub**. That link opens GitHub’s fine-grained PAT form with **Contents: write**, **Pull requests: write**, **Workflows: write**, resource owner, and a 7-day expiry already filled. **Workflows** is required to add `.github/workflows/agent.md` (GitHub Apps / `GITHUB_TOKEN` cannot create workflow files without it). On that form, set **Repository access** to **choose only the control repo `OWNER/something-org` — not all repositories, not the product repos**. Generate, copy, paste back into bellen. Open **Why your PAT is safe on this page.** on the form if you want the three-sentence safety note, or to do the same init **without** pasting a token (local `gh` or GitHub’s web editor).
5. Click **Create PR**. The page talks only to `api.github.com`. It opens branch `init/control-canvas` with:
   - `AGENTS.md`
   - `README.md` (short control-repo readme)
   - `.devcontainer/Dockerfile` (`FROM ghcr.io/e-st/bellen:<version>` — Dependabot)
   - `.devcontainer/devcontainer.json` (`image` = that tag, **no features**, **no onCreateCommand**, port **8000** only)
   - `.devcontainer/post-start.sh` (start Canvas, then clone product repos in the background)
   - removes leftover `.devcontainer/on-create.sh` if present
   - `.github/dependabot.yml` (image tag + Actions)
   - `.github/workflows/agent.md` (gh-aw stub)
   - `.github/workflows/update-from-bellen.yml` (**Update from bellen** button)
6. Workflow **`after-mastart-pr`** on the new repo comments a human checklist. It does **not** push workflow files (`GITHUB_TOKEN` is rejected). A human must still run `gh aw compile`.
7. Human, on **`OWNER/something-org`**:
   - Merge the PR.
   - Add secrets (see [Secrets](#7-secrets)).
   - Install a GitHub App on the **control repo and every product repo** (least privilege).
   - Create labels **`agent`** and **`canvas`**.
   - `gh extension install github/gh-aw` then `gh aw compile`, commit the generated `.lock.yml`.
8. **Code → Create codespace** on the control repo (not on a product repo).
9. After start: **Ports → 8000** (label `agent-canvas`, visibility **org**). No other port is forwarded. Preview should open; if not, open that port.
10. In Agent Canvas: enter `LOCAL_BACKEND_API_KEY`, set ACP to **`grok agent stdio`**, workspace **`/workspaces/platform`**.
11. Later: in the control repo, **Actions → Update from bellen → Run workflow**. That opens a PR with the latest image and control files (keeps `containerEnv.REPOS`). Merge, then **rebuild** the Codespace.

Revoke the initializer PAT after the PR exists. Codespaces uses your GitHub login to clone product repos you can already access.

## 5. Daily: `canvas` vs `agent`

File issues on the **control** repo. Apply **exactly one** of these labels:

| Label | When | Where it runs |
| --- | --- | --- |
| **`canvas`** | You will sit with the agent | Control Codespace → Canvas on port 8000 → `grok agent stdio` |
| **`agent`** | Unattended | GitHub Actions via gh-aw |

**Never both.** If both are present, stop and remove one.

The agent works in clones under `/workspaces/platform` and **pushes to the product remotes**. Those remotes are the source of truth.

## 6. Inspect

Do not prompt inside a product-repo editor. Open the product’s **own** Codespace (its own `.devcontainer`) on the agent branch:

```
https://codespaces.new/OWNER/PRODUCT?ref=agent/…
```

Example: if the agent pushed `agent/42-fix-login` to `OWNER/something`, inspect at `https://codespaces.new/OWNER/something?ref=agent/42-fix-login`.

VS Code is for reading the diff and running the product toolchain. Conversation stays in Canvas (interactive) or in the Actions log (unattended).

## 7. Secrets

Set these on **`OWNER/something-org`**. Codespace secrets apply to the control Codespace; Actions secrets apply to gh-aw.

| Secret | Where | Purpose |
| --- | --- | --- |
| **`XAI_API_KEY`** | Codespace + Actions | Grok Build / xAI |
| **`LOCAL_BACKEND_API_KEY`** | Codespace | Agent Canvas `--public` (paste it in the Canvas UI) |
| **`APP_ID`** | Actions | GitHub App id |
| **`APP_PRIVATE_KEY`** | Actions | GitHub App private key (`.pem` contents) |

Generate a strong `LOCAL_BACKEND_API_KEY` (for example `openssl rand -base64 32`) and store the same value as the Codespace secret and in your password manager. Anyone with that key and port 8000 can drive the control machine.

The App must be installed on the control repo **and** each product repo so Actions can open PRs where the code lives.

## 8. Security

- **Thin control image** — `ghcr.io/e-st/bellen`, built here from `mcr.microsoft.com/devcontainers/base:ubuntu` plus GitHub CLI, Node 22, uv, Grok Build, and `@openhands/agent-canvas`. No product SDKs. Dependabot on this repo updates those pins; Dependabot on each `*-org` repo bumps the image tag.
- **Port 8000 only** — `forwardPorts: [8000]`, other ports `onAutoForward: ignore`. Visibility `org`. Still require `LOCAL_BACKEND_API_KEY` (`--public`).
- **GitHub App least privilege** — only the control repo and its product repos; contents, issues, and pull requests. No org-wide install unless you intend that.
- **Initializer PAT** — fine-grained, one repo, Contents + Pull requests, short-lived. This Pages form never stores it; requests go to `api.github.com` only.
- **Do not commit** `.env` or `*.pem`. See `.gitignore`.

## 9. This repo’s file map

```
bellen/
├── README.md                              ← you are here (template docs)
├── AGENTS.md                              ← bellen is the template/pages repo
├── LICENSE                                ← MIT, Copyright (c) 2025-2026 e-St (same as e-St/fspure)
├── NOTICE                                 ← copyright + MIT pointer
├── .gitignore                             ← .env, *.pem, node_modules
├── image/
│   ├── Dockerfile                         ← control Codespace image
│   ├── package.json                       ← pins @openhands/agent-canvas (Dependabot)
│   └── VERSION                            ← ghcr.io/e-st/bellen tag
├── control/
│   ├── apply-update.sh                    ← used by Update from bellen
│   ├── render.py                          ← writes latest control files
│   ├── post-start.sh
│   └── dependabot.yml
├── docs/
│   ├── logo.jpg                           ← site mark (top of Pages)
│   ├── index.html                         ← GitHub Pages initializer
│   ├── legal.html                         ← license / contact / hosting
│   └── privacy.html                       ← static site + PAT form
└── .github/
    ├── dependabot.yml                     ← docker/npm for image/, Actions
    └── workflows/
        ├── after-mastart-pr.yml           ← checklist comment on init/* PRs
        ├── publish-image.yml              ← build/push ghcr.io/e-st/bellen
        └── update-from-bellen.yml         ← button: PR latest control files into *-org
```

Files the initializer writes live on **`OWNER/something-org`**, not here:

```
OWNER/something-org/
├── README.md                              ← short control-repo readme
├── AGENTS.md                              ← how to use that control repo
├── .devcontainer/Dockerfile               ← FROM ghcr.io/e-st/bellen:<version>
├── .devcontainer/devcontainer.json        ← port 8000 only; REPOS; PLATFORM
├── .devcontainer/post-start.sh            ← start Canvas, then clone REPOS
├── .github/dependabot.yml                 ← image tag + Actions
└── .github/workflows/
    ├── agent.md                           ← gh-aw stub (written by the initializer PAT)
    └── update-from-bellen.yml             ← Actions → Update from bellen
```

## License

MIT License. Copyright (c) 2025-2026 e-St. Same terms as [e-St/fspure](https://github.com/e-St/fspure): see [LICENSE](LICENSE) and [NOTICE](NOTICE).
