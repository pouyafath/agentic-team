# 7. Cost model

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

**Subscription alternative:** running sessions on a Claude subscription plan instead of API
keys swaps per-token billing for plan usage limits. The token profile above is still the right tool
for capacity planning. Use API keys when you need per-project cost attribution (M3 experiments).

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
