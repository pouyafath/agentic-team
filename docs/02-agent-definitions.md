# 2. Agent definitions

The executable definitions, including the full prompts, are in `.claude/agents/*.md`. This
document is the readable summary plus the handoff contracts. Write scopes and command limits are
enforced by `.claude/hooks/policy.json`.

## Roster

| Agent | Activation | Model · effort | Isolation | Writes | Branches | Turn cap |
|---|---|---|---|---|---|---|
| `pm` | always (main session) | Opus · high | main checkout | `docs/product/**` only | none | — |
| `developer` | every story | Sonnet · high | worktree | everything except CI, infra, acceptance tests, ADRs and contracts | `story/*` | 150 |
| `qa` | every story (design + verify) | Sonnet · high | worktree | `tests/acceptance/**`, `tests/regression/**`, `e2e/**` | `qa/*` | 100 |
| `reviewer` | every story | Opus · high (max for risk:2) | worktree, detached | nothing | none | 60 |
| `architect` | setup, major features, risk:2 | Opus · xhigh | worktree | `docs/**` | `design/*` | 80 |
| `devops` | CI/CD, releases, incidents | Sonnet · high | worktree | `.github/**`, `infra/**`, `deploy/**`, containers, runbooks, Makefile | `ops/*` | 80 |

**Model rationale:** reasoning-heavy, low-volume roles (orchestration, architecture,
security review) run on Opus. High-volume roles (implementation, testing) run on Sonnet,
which halves input and output prices. Cache reads cost the same on both (see
`docs/07-cost-model.md`). Running the reviewer on a different model than the developer
also adds diversity, so the reviewer is less likely to share the author's blind spots. Both
choices are hypotheses that configuration C4 in `docs/06-evaluation.md` tests.

**Always forbidden for every agent:** push to `main`, force-push, merge PRs, delete remote
branches, publish releases, deploy, manage secrets, read `.env*`, dump the environment, pipe
downloads into a shell, live payment operations, or edit guardrail files.

## Per-agent contracts

### PM / Orchestrator
- **Mission:** maximize delivered value at the required quality with minimal human toil.
- **Inputs:** PO ideas and answers; agent reports; GitHub state.
- **Outputs:** brief and epic issues, story issues (spec plus acceptance criteria), labels and
  state, briefs to agents, verdict comments posted on PRs, escalations, status updates.
- **Decides:** story split and order *within* PO-approved priorities, routing, fix vs escalate.
- **Never decides:** priorities, scope changes, technology with lasting cost, merges, releases.

### Developer
- **Inputs:** brief (story #, mode, branches, docs, findings).
- **Outputs:** commits on `story/<n>-<slug>`, draft PR with the template handoff, return report
  (`READY_FOR_VERIFICATION` | `BLOCKED`, head SHA, criteria → tests, commands run).
- **Done when:** `make ci` is green locally, every criterion is mapped to a test, the PR is updated, and the branch is released.

### QA
- **Inputs:** story spec, contracts (design-tests mode); plus head SHA and cycle (verify mode).
- **Outputs:** acceptance tests on `qa/<n>-<slug>` (design-tests); a verdict report with
  coverage per criterion, suite results, exploratory notes and reproducible defects (verify).
- **Independence:** derives tests from the spec, not the implementation; re-runs everything itself.

### Reviewer / Security
- **Inputs:** PR number, head SHA, story, risk tier, cycle.
- **Outputs:** verdict report with scanner results and severity-ranked findings
  (file:line, why, fix). Only `blocking` findings justify `CHANGES_REQUESTED`.
- **Independence:** a separate instance on a separate model, read-only, and deterministic tools come first.
  For risk:2, it lists what a qualified human must double-check.

### Architect
- **Inputs:** brief issue, epics, constraints, existing code.
- **Outputs:** `design/<slug>` PR with architecture notes, API contracts, ADRs (with
  alternatives), walking-skeleton spec, and a story breakdown with dependencies and risk tiers.

### DevOps / Release
- **Inputs:** ops request or release brief (version, stories, SHA).
- **Outputs:** `ops/<slug>` PRs for pipeline and infra changes; `RELEASE_READY` report with
  checklist (CI, staging at SHA, smoke, monitoring, rollback) and a **draft** release.

## Handoff contracts

| Handoff | From → To | Artifact | Required fields |
|---|---|---|---|
| Brief | PM → any | Agent prompt | story #, risk, mode, branches, head SHA, docs to read, task, findings |
| Implementation | Developer → PM | Return report + PR body | status, PR URL, head SHA, criteria→tests, commands run, disputes |
| Test design | QA → PM | Return report | branch, SHA, tests per criterion |
| Verification | QA → PM → PR comment | Verdict report | marker (story, agent, verdict, sha, cycle), coverage, defects |
| Review | Reviewer → PM → PR comment | Verdict report | marker, scanner results, findings with severity |
| Design | Architect → PM → PO | PR + report | ADRs, contracts, story breakdown, open questions |
| Release | DevOps → PM → PO | Report + draft release | checklist, staging URL, rollback |
| Escalation | PM → PO | Issue/PR comment | marker `ESCALATED`, summary, options, recommendation |

Verdict marker JSON schema (in the first line of every QA, review and escalation comment):

```json
{ "story": 12, "agent": "qa|reviewer|pm",
  "verdict": "PASS|FAIL|APPROVE|CHANGES_REQUESTED|BLOCKED|ESCALATED",
  "sha": "<40-hex head SHA>", "cycle": 1, "cost_usd": 1.42 }
```
`cost_usd` is optional. The PM adds it when the session reports usage.

## Human Product Owner

Owns: business goals and priorities (G1), architecture and technology approval (G2), every merge
(G3), production releases (G4), and any sensitive operation such as money, real users, production data,
credentials or legal matters (G5). The PO also arbitrates escalations and changes the guardrails
(maintenance mode: `AGENTIC_MAINTENANCE=1`).

## Specialist agents (activate per project)

Templates in `specialists/` are not loaded until you copy them into `.claude/agents/` and
add a `policy.json` entry. They advise and review; they do not replace qualified legal,
compliance or security professionals.

| Specialist | Use for | Typical write scope |
|---|---|---|
| `music-ml` | music information retrieval, audio features and embeddings, similarity, recommendation and playlist algorithms, offline evaluation | `ml/**`, `docs/ml/**` |
| `finance-domain` | money math and rounding, currencies, categorization, budgeting rules, bank-data integrations (aggregators), privacy | `docs/domain/**` (advisory) |
| `payments-compliance` | payment provider integration patterns, PCI scope minimization, idempotency, webhooks, reconciliation, fraud signals | `docs/payments/**` (advisory) |

Scaling the developer role (second developer, frontend and backend split) follows
`docs/04-workflow.md` §Scaling and needs evidence from `docs/06-evaluation.md`.
