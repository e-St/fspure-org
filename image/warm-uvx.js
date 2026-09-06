#!/usr/bin/env node
// Pre-download the same uvx stacks agent-canvas starts, so Codespace start is a cache hit.
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const root = path.join(
  execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim(),
  "@openhands/agent-canvas"
);
const d = JSON.parse(fs.readFileSync(path.join(root, "config/defaults.json"), "utf8"));
const v = d.versions.agentServer;
const acp = d.constraints && d.constraints.agentClientProtocol;

const agent = [
  "uvx",
  "--from",
  d.packages.agentServer + "==" + v,
  "--with",
  "openhands-sdk==" + v,
  "--with",
  "openhands-tools==" + v,
  "--with",
  "openhands-workspace==" + v,
];
if (acp) agent.push("--with", acp);
agent.push("--with", "posthog>=6,<7", "agent-server", "--help");
execFileSync(agent[0], agent.slice(1), { stdio: "inherit" });

execFileSync(
  "uvx",
  ["--from", d.packages.automation + "==" + d.versions.automation, "uvicorn", "--help"],
  { stdio: "inherit" }
);
