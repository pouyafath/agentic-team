# 5. MVP implementation plan

Principle: prove the smallest team end-to-end on a low-risk app, measure, then grow.

## Milestones

| | Goal | Deliverables | Exit criteria |
|---|---|---|---|
| **M0 Bootstrap** *(this kit, done)* | Team defined as code | 6 agent definitions, CLAUDE.md, guard + policy (tested), playbooks, issue/PR templates, CI and deploy templates, metrics script, design docs 01-07 | Kit tests green (`make ci`); PO has reviewed the docs |
| **M1 Pilot** | One feature, idea to staging, through every gate | Pilot repo from template; `setup-github.sh --protect`; `/kickoff` → design PR → backlog; walking skeleton + CI + staging; 1-2 product stories via `/deliver`; `/release` to staging | ≥1 story from idea to staging with QA PASS, APPROVE, green CI, gated merge; zero guardrail bypasses; metrics produced |
| **M2 Harden** | Make it reliable and cheap | Prompt and playbook fixes from M1 failure log; separate agent GitHub identity (bot or app) for a clean audit trail; usage telemetry (Console per-project key or OTel); optional `@claude` Action for event-driven runs | 5-10 stories delivered; ≥70% stories pass in ≤2 cycles; escalations ≤1 per 5 stories; cost per story within the doc-07 estimate ±50% |
| **M3 Experiments** | Choose the smallest team that works | Benchmark backlog with held-out tests; run C1-C5 (doc 06) | Decision record (ADR) naming the default configuration with evidence |
| **M4 Scale** | Parallelism and domains | Second developer if C3 wins; first specialist agent for the next real project (music, finance, or payments) | Throughput up with no quality regression; specialist findings adopted in ≥1 design |
| **M5 Autonomy (optional)** | Less human toil where safe | (Autonomous merge already adopted.) Event-driven delivery via GitHub Action; durable orchestrator only if unattended multi-story runs are needed | Escaped-defect rate unchanged over 4 weeks after the change |

## Recommended pilot application

Low-risk, but realistic enough to exercise every role: UI + API + persistence + one
external read-only integration, with **no real money and no sensitive personal data**.

Good options, all aligned with your target domains:

1. **Playlist curator (music, recommended):** create playlists from a local catalog,
   tag tracks by mood or tempo, generate a playlist from rules (for example, "60 minutes, rising
   energy"). Later stories can add audio-feature analysis (music-ml specialist) without any
   payment or PII risk.
2. **Expense tracker with fake data:** CSV import, categorization, monthly budget view.
   Exercises money math (risk:2 practice) with synthetic data only.
3. **Subscription billing in test mode:** a payment provider's sandbox only. Exercises
   payments patterns safely, but save it for after M2, since it is the highest-risk domain.

You said you will hand over the first project. If it is a payment or financial app, we can
still start there, but the first milestone should be a sandbox-only slice with synthetic data,
and every money-handling story runs as risk:2.

## Plan risks and mitigations

| Risk | Mitigation |
|---|---|
| Agents over-escalate or under-escalate | Tune the PM prompt with M1 examples; track escalations per story |
| Rework loops burn tokens | 3-cycle cap; CI must be green before verification; small stories |
| QA tests coupled to guessed interfaces | Architect publishes contracts first; the developer can dispute tests |
| Autonomous merges let a bad change reach staging | SHA-bound gate + required checks + staging smoke tests; production still human-approved; watch escaped defects weekly and turn on `risk2_human_merge` if they rise |
| Hooks are not a hard boundary | Hard boundaries come from GitHub (protection, environments) and credential separation |
| Vendor or tool changes | Tool-agnostic contracts; quarterly re-assessment of doc 03 |
