# 3. Technology assessment

> **Disclosure.** This assessment was written by Claude, running inside Claude Code, which is one
> of the candidates. The recommendation is partly practical (it is the runtime this team will
> run in from day one), but you should weigh it with that in mind. The evaluation plan
> (`docs/06-evaluation.md`) includes a cross-vendor configuration, so the choice gets tested
> rather than assumed. Facts below were checked against vendor documentation or recent coverage
> in October 2026. Re-verify before any long-term commitment, because this market moves monthly.

## What we actually need to buy or build

| Need | Category |
|---|---|
| An agent that can read, edit, run and test code in a repo | **Coding agent** |
| Role specialization (prompts, tools, models, permissions per role) | Coding agent or orchestration framework |
| Sequencing, parallelism, retries, durable state, human-in-the-loop | **Orchestration** |
| Backlog, status, review threads, audit trail | **Work tracking** |
| Deterministic checks, deploys, release approvals | **CI/CD** |

## Criteria

Fit to need, maturity and stability, human-oversight support (approvals, permissions, audit),
customization effort, operational burden, cost, lock-in.

## Candidates

| Candidate | What it is | Strengths for us | Weaknesses for us | Verdict |
|---|---|---|---|---|
| **Claude Code** | Coding agent (CLI, IDE, desktop, cloud sessions), plus GitHub Action and Agent SDK built on the same harness | Subagents with per-agent prompt, tools, model, effort, turn cap and **git-worktree isolation**; PreToolUse **hooks** that see which subagent is acting; permission rules; skills as playbooks; cloud sessions; `claude-code-action@v1` for event-driven runs | Orchestration is LLM-driven (the PM agent), not a deterministic state machine; tied to Anthropic models; durability depends on external state, which we deliberately put in GitHub | **Adopt (v1 runtime)** |
| **OpenAI Codex** | Coding agent: open-source CLI, IDE, desktop, cloud tasks in isolated containers, GitHub PR review | Strong independent coding agent; cloud tasks open PRs; review in GitHub; bundled with ChatGPT plans (credit-based since 2026) | A second runtime doubles the permission and config surface; we did not verify its current multi-agent role features; some cloud features reportedly require ChatGPT-plan auth rather than API keys | **Trial (M3)** as a cross-vendor second reviewer for risk:2 |
| **LangGraph** | Stateful graph orchestration library (v1.0, Oct 2025) with checkpointed durable execution and human-in-the-loop interrupts | Deterministic workflows, resume after failure, multi-day approvals, mature observability (LangSmith) | Not a coding agent: you wrap one (for example, Claude Agent SDK) as nodes; you build, host and operate the service | **Assess (M5)** if we need unattended, durable pipelines |
| **Microsoft Agent Framework** | Open-source agent and workflow SDK (.NET and Python), GA as 1.0 in April 2026; successor to Semantic Kernel + AutoGen | Typed workflows, multi-provider (including Claude), MCP and A2A interop, long-term support, strong in Azure/.NET shops | Same as LangGraph (orchestration, not coding); heavier if you are not in the Microsoft ecosystem | **Assess (M5)** as the LangGraph alternative for .NET/Azure |
| **GitHub Actions** | CI/CD | Deterministic gates agents can't bypass; environments with required reviewers; secrets isolation; free for public repos | Minutes cost on private repos at scale | **Adopt** |
| **GitHub Issues / Projects** | Work tracking | System of record humans already use; labels as workflow states; API and `gh` CLI; Projects as a Kanban view | Labels are a weak state machine (mitigated by the PM and `/board` checks) | **Adopt** (Issues + labels; Projects optional view) |

## Recommended stack

| Layer | Choice | Build vs buy |
|---|---|---|
| Coding agents and roles | Claude Code subagents | Buy/reuse; we write only prompts |
| Orchestration (v1) | PM agent + playbooks + GitHub state | ~4 playbook files |
| Guardrails | Claude Code hooks/permissions + GitHub branch protection, CODEOWNERS, environments | ~150-line policy guard |
| Tracking | GitHub Issues + labels (+ Projects view) | Reuse |
| CI/CD and security scanning | GitHub Actions + gitleaks + Semgrep + dependency review + ecosystem audit | Reuse |
| Metrics | GitHub data + Console/OTel usage | ~200-line script |
| Event-driven runs (M2+) | `anthropics/claude-code-action@v1` | Reuse |
| Durable orchestration (only if needed) | Claude Agent SDK workers + LangGraph or MS Agent Framework | Build later, on evidence |

## Why not start with LangGraph or Agent Framework?

Both are good at orchestration and neither is a coding agent. Starting there means building
tool execution, repo access, sandboxing and permission handling that a coding agent already has.
A supervised team with a human in the loop every day does not need a durable server-side state
machine yet, because GitHub already holds the state. We revisit when the metrics show we need unattended,
long-running, multi-story automation (milestone M5).

## Lock-in mitigation

All contracts (issue templates, verdict markers, branch conventions, `make` targets, CI) are
tool-agnostic. Swapping the agent runtime means rewriting six prompt files and the hook adapter.
Backlog, history, gates and metrics are unaffected.

## Sources

- Claude Code docs: [subagents](https://code.claude.com/docs/en/sub-agents), [hooks](https://code.claude.com/docs/en/hooks), [settings](https://code.claude.com/docs/en/settings), [GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Microsoft Agent Framework 1.0 announcement](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)
- LangGraph 1.0 coverage: [LangChain changelog](https://changelog.langchain.com/announcements/ann_lxOZRCoFw2Qn9), [overview of durable execution](https://learn.traeai.com/t/ai-engineering/phases/14-agent-engineering/13-langgraph-stateful-graphs.html)
- Codex: third-party 2026 reviews ([skillscouter](https://skillscouter.com/codex-review/), [eesel](https://www.eesel.ai/de/blog/openai-codex-preise)). Verify against OpenAI's docs before adopting.
