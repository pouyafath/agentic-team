# Agentic Software Development Team

A reusable, supervised team of AI agents that takes software from idea to tested, reviewed,
staging-deployed code. It runs on Claude Code and GitHub and stays accountable to a human
Product Owner (you).

**The team:** PM/Orchestrator · Full-stack Developer · QA Engineer · Code Reviewer/Security,
plus an Architect and a DevOps/Release engineer on demand, plus optional domain specialists
(music ML, personal finance, payments).

**Design principle:** start with the smallest team that does independent verification, keep
humans on every irreversible decision, and grow only when the metrics say so.

## How it works

```
You ──idea──▶ PM ──briefs──▶ Developer ∥ QA(test-first) ──PR──▶ CI ──▶ QA(verify) ∥ Reviewer
 ▲                                                                          │
 └──── release approval (G4) ◀── staging ◀── PM merges (G3) ◀── PASS + APPROVE + CI on same SHA
```

- **State lives in GitHub:** issues are the backlog, labels are the workflow, PRs are the work,
  and verdict comments are the handoffs. Sessions are disposable; `/board` resumes anywhere.
- **Independent verification:** QA writes acceptance tests from the spec before or while the
  developer codes, then re-verifies the exact commit. A read-only reviewer on a different model
  checks correctness and security. Verdicts are bound to a commit SHA.
- **Least privilege, enforced:** a PreToolUse hook gives each role its own write scope and
  lets only the PM merge (SHA-bound, never `--admin`), and blocks force-pushes, deploys, secret
  access and guardrail edits, in every permission mode.
- **Humans decide:** scope (G1), architecture (G2), production (G4),
  and anything involving money, real users, production data or credentials (G5). Merging (G3)
  is automated behind the gate.

## Quick start

1. **Create the project repo:** use this repository as a GitHub template, or run
   `scripts/install.sh /path/to/existing-repo`.
2. **Configure GitHub (you, once):** `scripts/setup-github.sh --protect` creates labels,
   fills CODEOWNERS, and protects `main`. Then create `staging` and `production` environments, with
   yourself as the required reviewer on production.
3. **Start a Claude Code session** in the repo (CLI: `claude --agent pm`, or a cloud session) and run:
   - `/kickoff <your product idea>`: brief → design PR → prioritized backlog
   - `/deliver <issue#>`: one story through implementation, QA and review
   - `/release v0.1.0`: staging verification and a draft release for your approval
   - `/board`: status, what's waiting on you, and the next action

## What's in the box

```
CLAUDE.md                     team operating rules (loaded by every agent)
.claude/agents/               pm, developer, qa, reviewer, architect, devops
.claude/skills/               /kickoff /deliver /release /board playbooks
.claude/hooks/guard.py        role-based guardrail (+ policy.json), tested
.claude/settings.json         hook wiring, secret-file deny rules, no nested agents
.github/                      story/bug forms, PR handoff template, CODEOWNERS,
                              CI gates (make ci, gitleaks, Semgrep, dependency review),
                              gated deploys (staging auto, production human-approved)
specialists/                  music-ml, finance-domain, payments-compliance (opt-in)
scripts/                      setup-github.sh, install.sh, metrics.py (+ tests)
docs/                         design deliverables (below), ADRs, runbooks
```

## Design deliverables

| # | Document | Answers |
|---|---|---|
| 1 | [Architecture proposal](docs/01-architecture.md) | system design, orchestration, communication, state, trust boundaries |
| 2 | [Agent definitions](docs/02-agent-definitions.md) | roles, tools, permissions, models, inputs/outputs, handoff contracts |
| 3 | [Technology assessment](docs/03-technology-assessment.md) | Claude Code vs Codex vs LangGraph vs MS Agent Framework; recommended stack |
| 4 | [Workflow design](docs/04-workflow.md) | lifecycle, gates, risk tiers, failure handling, scaling |
| 5 | [MVP plan](docs/05-mvp-plan.md) | milestones M0-M5, exit criteria, pilot choice |
| 6 | [Evaluation framework](docs/06-evaluation.md) | metrics, experiment design, decision rule |
| 7 | [Cost model](docs/07-cost-model.md) | token profile, $/story, monthly scenarios, cost controls |
| — | [ADR-0001](docs/adr/0001-claude-code-subagents-on-github.md) | why this stack for v1 |

## Maintaining the guardrails

Agents cannot edit `.claude/`, `CLAUDE.md` or CODEOWNERS. To change them, launch Claude Code with
`AGENTIC_MAINTENANCE=1` (or edit by hand), then run `make ci`. The guard's tests live in
`scripts/tests/`. The hook is a guardrail against mistakes. The hard boundaries are GitHub branch
protection, environment approvals, and keeping production credentials out of agent environments.

## Status

M0 (bootstrap) is complete. Next: M1, a pilot project end-to-end. See [docs/05-mvp-plan.md](docs/05-mvp-plan.md).
