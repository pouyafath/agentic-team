# ADR-0001: Claude Code subagents with GitHub as system of record for v1

- **Status:** proposed (awaiting PO approval)
- **Deciders:** architect (proposal), Product Owner (approval)

## Context
We need a small, supervised agentic team (PM, developer, QA, reviewer, plus architect and devops on
demand) that can deliver real software repeatedly. It needs independent verification, least
privilege, human approval gates, traceability, and low build and operating cost. Sessions run in
ephemeral containers, so state must survive outside the agent runtime.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A. Claude Code subagents + GitHub (issues, PRs, Actions, environments) | Coding, roles, worktree isolation, hooks and permissions built in; durable state in a system humans already use; near-zero infrastructure | LLM-driven orchestration; Anthropic-model dependency |
| B. LangGraph orchestrator + Agent SDK workers | Deterministic, durable state machine; checkpointed recovery | Must build and host the service, tools and permissions; weeks of work before the first story |
| C. Microsoft Agent Framework workflows | Typed workflows, multi-provider, enterprise support | Same build burden as B; best fit for .NET/Azure |
| D. Single general-purpose agent | Cheapest and simplest | No independent verification, which fails the core requirement |

## Decision
Option A. It delivers every required capability with the least custom code, and putting all state
in GitHub keeps B or C available later without changing contracts or history.

## Consequences
- Custom code is limited to prompts, `guard.py` and `policy.json`, playbooks, and `metrics.py`.
- Hooks are guardrails, not a security boundary. GitHub protections and credential separation are.
- Revisit at M5, or earlier if we need unattended multi-story runs (then B or C with Agent SDK workers).
