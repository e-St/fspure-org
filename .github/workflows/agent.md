---
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
Do not treat clones under `/workspaces/platform` as a substitute for those remotes.

Product repos:

- e-St/fspure
- e-St/fspure-ready-lib
- e-St/fstarter

Human: `gh extension install github/gh-aw && gh aw compile`
