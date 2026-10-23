#!/usr/bin/env python3
"""PreToolUse guardrail for the agentic team.

Claude Code runs this before every Bash, Edit, Write, MultiEdit and NotebookEdit call
and passes the call as JSON on stdin. Subagent calls carry `agent_type`. Exit code 2
blocks the call and shows stderr to the agent. The policy lives in policy.json.

The guard catches mistakes and keeps roles honest. It is not a sandbox: the real
boundaries are GitHub branch protection, CODEOWNERS, environment approvals and
keeping production credentials out of agent environments.

Set AGENTIC_MAINTENANCE=1 in the environment that launches Claude Code to let a human
edit protected files and lift per-role write scopes. Global command rules always apply.
"""
import fnmatch
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POLICY_FILE = os.path.join(HERE, "policy.json")
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def load_policy(path=POLICY_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def repo_root(path):
    """Closest ancestor holding a .git entry (a dir, or a file in worktrees)."""
    d = os.path.abspath(path)
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def matches(rel, patterns):
    return any(fnmatch.fnmatchcase(rel, p) for p in patterns)


def role_rules(policy, agent):
    if not agent:
        return policy.get("main", {})
    return policy["agents"].get(agent, policy.get("unlisted_agents", {}))


def check_write(policy, agent, path, maintenance):
    root = repo_root(path)
    if root is None:
        return None  # outside any repository (scratch files)
    rel = os.path.relpath(os.path.abspath(path), root).replace(os.sep, "/")
    if maintenance:
        return None
    if matches(rel, policy.get("protected_paths", [])):
        return (f"'{rel}' is a protected guardrail file. Only the human Product Owner "
                "changes it (maintenance mode).")
    rules = role_rules(policy, agent)
    allow = rules.get("write_allow")
    deny = rules.get("write_deny", [])
    who = f"agent '{agent}'" if agent else "the main (PM) session"
    if matches(rel, deny) or (allow is not None and not matches(rel, allow)):
        hint = ("Delegate the change to the owning role agent." if not agent or agent == "pm"
                else "This path belongs to another role; report it to the PM.")
        scope = f"allowed: {allow or 'nothing'}" + (f", except: {deny}" if deny else "")
        return f"{who} may not write '{rel}' ({scope}). {hint}"
    return None


def check_bash(policy, agent, command, maintenance):
    cmd = " ".join(command.split())
    rules = list(policy.get("bash_deny", []))
    if agent:
        rules += policy["agents"].get(agent, {}).get("bash_deny", [])
    if not maintenance:
        rules += policy.get("bash_deny_unless_maintenance", [])
    for rule in rules:
        if re.search(rule["pattern"], cmd):
            return rule["reason"]
    return None


def decide(event, policy, maintenance=False):
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    agent = event.get("agent_type") or None
    if tool == "Bash":
        return check_bash(policy, agent, tool_input.get("command", ""), maintenance)
    if tool in WRITE_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not path:
            return None
        if not os.path.isabs(path):
            path = os.path.join(event.get("cwd") or os.getcwd(), path)
        return check_write(policy, agent, path, maintenance)
    return None


def main():
    try:
        event = json.load(sys.stdin)
        reason = decide(event, load_policy(), os.environ.get("AGENTIC_MAINTENANCE") == "1")
    except Exception as exc:  # fail closed: a broken guard must not wave calls through
        print(f"guardrail error ({exc!r}); call blocked. Ask the PO to check .claude/hooks.",
              file=sys.stderr)
        sys.exit(2)
    if reason:
        print(f"Blocked by team guardrail: {reason}", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
