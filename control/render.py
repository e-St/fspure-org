#!/usr/bin/env python3
"""Write bellen control files into ROOT, keeping containerEnv.REPOS."""
import json
import os
import pathlib
import shutil
import sys

ROOT = pathlib.Path(os.environ.get("ROOT", ".")).resolve()
BELLEN = pathlib.Path(os.environ.get("BELLEN", "")).resolve()
if not BELLEN.joinpath("image/VERSION").is_file():
    sys.stderr.write("BELLEN must point at an e-St/bellen checkout (image/VERSION missing).\n")
    sys.exit(1)

IMAGE = "ghcr.io/e-st/bellen:" + BELLEN.joinpath("image/VERSION").read_text().strip()
CONTROL = BELLEN / "control"


def repo_id():
    spec = os.environ.get("GITHUB_REPOSITORY") or ""
    if "/" in spec:
        return spec.split("/", 1)
    remote = ""
    git = ROOT / ".git" / "config"
    if git.is_file():
        text = git.read_text()
        for line in text.splitlines():
            if "github.com" in line and "url" in line:
                remote = line.split("=", 1)[-1].strip()
                break
    remote = remote.replace("git@github.com:", "").replace("https://github.com/", "").replace(".git", "").strip("/")
    if "/" in remote:
        return remote.split("/", 1)
    return "OWNER", ROOT.name


def load_env():
    path = ROOT / ".devcontainer" / "devcontainer.json"
    repos, platform = "", "/workspaces/platform"
    if path.is_file():
        data = json.loads(path.read_text())
        env = data.get("containerEnv") or {}
        repos = (env.get("REPOS") or "").strip()
        platform = (env.get("PLATFORM") or platform).strip() or platform
    return repos, platform


def repos_md(repos_csv):
    items = [s.strip() for s in repos_csv.split(",") if s.strip()]
    if not items:
        return "- (none listed yet)"
    return "\n".join("- `%s`" % r for r in items)


def repos_agent(repos_csv):
    items = [s.strip() for s in repos_csv.split(",") if s.strip()]
    if not items:
        return "- (none listed in containerEnv.REPOS)"
    return "\n".join("- %s" % r for r in items)


def write(path: pathlib.Path, body: str, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body if body.endswith("\n") else body + "\n")
    os.chmod(path, mode)


def main():
    owner, name = repo_id()
    repos_csv, platform = load_env()
    dc = {
        "name": "control",
        "image": IMAGE,
        "containerEnv": {"REPOS": repos_csv, "PLATFORM": platform},
        "forwardPorts": [8000],
        "portsAttributes": {
            "8000": {
                "label": "agent-canvas",
                "onAutoForward": "openPreview",
                "visibility": "org",
            }
        },
        "otherPortsAttributes": {"onAutoForward": "ignore"},
        "postStartCommand": "bash .devcontainer/post-start.sh",
        "waitFor": "postStartCommand",
    }
    write(
        ROOT / ".devcontainer" / "Dockerfile",
        '# Keep devcontainer.json "image" on this same tag.\nFROM %s\n' % IMAGE,
    )
    write(ROOT / ".devcontainer" / "devcontainer.json", json.dumps(dc, indent=2) + "\n")
    shutil.copyfile(CONTROL / "post-start.sh", ROOT / ".devcontainer" / "post-start.sh")
    os.chmod(ROOT / ".devcontainer" / "post-start.sh", 0o755)
    (ROOT / ".github").mkdir(parents=True, exist_ok=True)
    (ROOT / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CONTROL / "dependabot.yml", ROOT / ".github" / "dependabot.yml")
    on_create = ROOT / ".devcontainer" / "on-create.sh"
    if on_create.exists():
        on_create.unlink()

    update_url = "https://github.com/%s/%s/actions/workflows/update-from-bellen.yml" % (owner, name)
    list_md = repos_md(repos_csv)
    write(
        ROOT / "README.md",
        """# {name}

Thin **control** repo (`{owner}/{name}`). Product code is not here.
Created from [bellen](https://github.com/e-St/bellen).

## Update from bellen

[{update_url}]({update_url}) → **Run workflow**. That opens a PR with the latest control image and files. Your product repo list is kept. Merge the PR, then **rebuild** the Codespace.

## Codespace

1. Code → Create codespace on `main` (after merge). Image: `{image}`.
2. Wait for start (Agent Canvas on port 8000, then product clones).
3. Ports → **8000** (`agent-canvas`, visibility org). Only this port is forwarded.
4. Paste `LOCAL_BACKEND_API_KEY` in the Canvas UI (Codespace secret, or `$HOME/.openhands/local-backend-api-key` if unset).
5. ACP command: `grok agent stdio`
6. Workspace: `{platform}`

Product repos cloned there:

{list_md}

## Labels

| Label | Meaning |
| --- | --- |
| `agent` | Unattended gh-aw on Actions. |
| `canvas` | Interactive Canvas in this Codespace. |

Never apply both to the same issue. File issues on this control repo.

## Inspect

Do not prompt in a product editor. Open the product repo's own Codespace:

`https://codespaces.new/OWNER/PRODUCT?ref=agent/…`
""".format(
            name=name,
            owner=owner,
            update_url=update_url,
            image=IMAGE,
            platform=platform,
            list_md=list_md,
        ),
    )
    write(
        ROOT / "AGENTS.md",
        """# {name}

This is the thin control repo `{owner}/{name}`.
Product code lives in separate repos. Git is the shared disk.

On Codespace start, product repos are cloned under `{platform}` from `containerEnv.REPOS`:

{list_md}

## Labels

- `agent` — unattended work via gh-aw on GitHub Actions. Never combine with `canvas`.
- `canvas` — interactive work in this control Codespace (Agent Canvas). Never combine with `agent`.

## Interactive (`canvas`)

1. Codespace on **this** repo (not a product repo).
2. Port 8000 only — Agent Canvas, visibility org. Image `{image}`.
3. ACP: `grok agent stdio`
4. Workspace: `{platform}`

Do not prompt inside a product-repo editor. Humans inspect:

`https://codespaces.new/OWNER/PRODUCT?ref=agent/…`

## Unattended (`agent`)

Issues labeled `agent` on this repo run `.github/workflows/agent.md` after a human has run `gh aw compile`.
Push to the product remotes. Open PRs there.
""".format(
            name=name, owner=owner, platform=platform, list_md=list_md, image=IMAGE
        ),
    )
    items = [s.strip() for s in repos_csv.split(",") if s.strip()]
    agent_list = "\n".join("- %s" % r for r in items) if items else "- (none listed in containerEnv.REPOS)"
    write(
        ROOT / ".github" / "workflows" / "agent.md",
        """---
# gh-aw source stub. Human: install the extension, choose an engine, set secrets, then run: gh aw compile
on:
  issues:
    types: [labeled]
permissions: read-all
---

# Agent

Run only when the issue has the `agent` label and does **not** have `canvas`.
Never apply both labels.

Work the issue in the product repositories. Git is the shared disk.
Open a PR on the product repo (branch like `agent/<n>-short-slug`).
Do not treat clones under `{platform}` as a substitute for those remotes.

Product repos:

{agent_list}

Human: `gh extension install github/gh-aw && gh aw compile`
""".format(platform=platform, agent_list=agent_list),
    )
    print("Wrote control files for %s/%s image=%s repos=%s" % (owner, name, IMAGE, repos_csv or "(none)"))


if __name__ == "__main__":
    main()
