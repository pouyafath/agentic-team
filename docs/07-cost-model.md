# 7. Cost model

> **Billing mode for this team: the PO's Claude subscription (default).** Sessions in Claude
> Code (cloud, CLI, desktop), including every subagent they spawn, draw on the subscription's usage
> limits instead of per-token API billing. The dollar figures below then translate into **how much
> of your plan's usage a story consumes**, not an invoice. API keys are optional, for when you need
> hard per-project cost attribution (M3 experiments) or capacity beyond the plan.

All numbers are **estimates for planning**. They must be calibrated with real usage in M1 and M2.
Real token counts commonly vary 2-3× with codebase size, story clarity, and effort level.

## Prices used (Claude API, USD per million tokens, as of October 2026)

| Model | Input | Cache write* | Cache read | Output | Used by |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 4.00 | 5.00 | 0.20 | 20.00 | PM, reviewer, architect |
| Claude Sonnet 5.5 | 2.00 | 2.50 | 0.20 | 10.00 | developer, QA, devops |
| Claude Haiku 5.5 | 0.10 | — | — | 0.50 | (optional cheap helpers) |
| Claude Fable 5.1 | 10.00 | — | 0.25 | 50.00 | not used by default (hardest decisions only, by PO choice) |

\*Cache write is assumed at 1.25× input (5-minute cache). Longer cache lifetimes cost more to write.
Check current prices at https://claude.com/platform/api before budgeting. Thinking tokens bill as output.

Agentic coding is dominated by **re-reading context every turn**. Prompt caching turns most of
that into cache reads at about 5-10% of the input price, which is why cache reads appear as the largest
token volume but not the largest cost.

## Token profile per medium story (first pass)

A medium story is roughly one UI and one API slice with persistence, 300-800 changed lines.

| Agent | Model | Fresh input / cache writes | Cache reads | Output | Cost |
|---|---|---|---|---|---|
| PM (orchestration) | Opus | 60k | 1.0M | 20k | $0.90 |
| Developer | Sonnet | 200k | 6.8M | 120k | $3.06 |
| QA, design tests | Sonnet | 60k | 1.0M | 30k | $0.65 |
| QA, verify | Sonnet | 100k | 2.4M | 40k | $1.13 |
| Reviewer | Opus | 100k | 2.1M | 30k | $1.52 |
| **First pass** | | | | | **$7.26** |
| Fix cycle (dev 40%, QA verify, review 60%, PM) | | | | | $3.59 |
| **Expected, at 0.5 fix cycles per story** | | | | | **≈ $9** |

## Per-story and per-project estimates

| Item | Estimate | Range |
|---|---|---|
| Small story (risk:0/1, under 200 lines) | ~$3 | $1.50-6 |
| Medium story | ~$9 | $6-15 |
| Large story (should usually be split) | ~$22 | $15-40 |
| Project kickoff (PM brief + architect design + devops CI/staging + walking skeleton) | ~$20 | $15-35 one-off |
| Release (devops prep + PM) | ~$2 | $1-4 |

**Configuration comparison (medium story, expected):**

| Config | Est. cost | Note |
|---|---|---|
| C1 single agent, no independent verification | ~$5-6 | Cheapest per story; cost of escaped defects not included |
| C2 default (tiered models) | ~$9 | Proposed |
| C4 all-Opus | ~$12.50 (+38%) | Less than 2× because cache reads cost the same on both models; may need fewer cycles |
| C5 add cross-vendor reviewer on risk:2 | +$1.5-3 per risk:2 story | Depends on the vendor plan |

## Monthly scenarios (API billing)

| Scenario | Stories per week (S/M/L) | LLM cost per month |
|---|---|---|
| Pilot (M1-M2) | 5 (2/2/1) | ~$220 |
| Steady, 1 developer | 10 (4/5/1) | ~$360 |
| Scaled, 2 developers | 18 (7/9/2) | ~$660 |

These include PM planning (~$3 per week) and weekly releases. Add the one-off kickoff cost per new project.

**Non-LLM costs:**
- **GitHub Actions:** ~20-70 runner-minutes per story (3-4 jobs × 2-3 pushes). Free on public
  repos. Private repos draw from the plan's monthly allowance, so check your plan at the
  "Scaled" volume.
- **Staging hosting:** usually $0-30 per month on a small PaaS or free tier for a pilot app.
- **Third-party sandboxes** (payment providers, music APIs): typically free in test mode.

## Running on a Claude subscription (default)

- **What uses the plan:** interactive and cloud Claude Code sessions, including subagents. The
  Claude Code GitHub Action can also run on the plan through a `CLAUDE_CODE_OAUTH_TOKEN`
  secret (generated with `claude setup-token`; available on Pro, Max, Team and Enterprise).
- **What changes:** the constraint becomes plan usage limits (rolling and weekly windows), not
  dollars. Opus-heavy work uses the allowance faster, so model tiering by role still matters
  because it raises how many stories fit in a window.
- **Throughput planning:** treat the per-story estimates above as relative weights (small ≈ 1,
  medium ≈ 3, large ≈ 7). In M1, record how many stories of each size fit in a usage window,
  and plan WIP from that.
- **When limits bite:** the PM pauses at a clean point (work is pushed, and state is in GitHub)
  and resumes in the next window with `/board`. Alternatives: lower effort on routine roles, move
  QA and devops to Sonnet at medium effort, or add an API key for overflow.
- **Trade-off:** no per-project dollar attribution. `scripts/metrics.py` still reports cycles,
  throughput and quality, so cost comparisons in M3 use tokens or a dedicated API key.

## Cost controls (built in)

1. **Model tiering by role:** Sonnet for high-volume roles; Opus where judgment matters.
2. **Effort per agent** in frontmatter; raise only with evidence (risk:2 reviewer → max).
3. **Turn caps** (`maxTurns`) per agent: developer 150, QA 100, architect and devops 80, reviewer 60.
4. **Rework cap:** 3 cycles, then escalation instead of looping.
5. **CI before verification:** QA and review never spend tokens on a red build.
6. **Small stories:** the PM splits anything over about one day or 800 lines.
7. **Lean, cache-friendly context:** short CLAUDE.md, reference-only briefs, capped
   reports, fresh PM sessions per work block, resume (not restart) for fix rounds.
8. **Tier-based depth:** risk:0 skips QA test design; the reviewer runs at medium effort.
9. **Hard spend limits:** a Console workspace or key per project with a monthly limit;
   CI `timeout-minutes` and `concurrency` on every job.
10. **Weekly review:** cost per accepted story in the PM's planning comment; investigate
    outliers above 2× the estimate.

## Calibration plan

M1: record actual usage per story (Console per-key usage or OTel) next to the table above.
M2: replace the estimates with the measured medians and ranges, and set the per-project budget
at 1.3× the measured monthly run-rate.
