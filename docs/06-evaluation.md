# 6. Evaluation framework

Goal: find the **smallest team configuration that consistently delivers high-quality software at
acceptable cost and speed**, using measurements rather than assumptions.

## Metrics

| Dimension | Metric | Definition | Source |
|---|---|---|---|
| Productivity | Throughput | Stories done per week | `scripts/metrics.py` (issues) |
| | Lead time | Story created → closed (median, hours) | issues |
| | PR cycle time | PR opened → merged (median) | PRs |
| Quality | First-pass yield | Share of done stories with QA PASS and APPROVE in cycle 1 | verdict markers |
| | Defects caught before merge | QA FAIL + CHANGES_REQUESTED verdicts | verdict markers |
| | Escaped defects per story | Bugs found in staging or production (or `defect:escaped`) / done stories | bug issues |
| | Held-out test pass rate *(experiments)* | Share of PO-held acceptance tests passing at merge | benchmark harness |
| | Review quality *(experiments)* | Rubric score, 1-5, by a blinded human (correctness, clarity, security, tests) | grading sheet |
| Efficiency | Cost per accepted story | API cost / done stories | Console usage per project key, OTel, or `cost_usd` in markers |
| | Tokens per accepted story | Same, in tokens, split by agent | OTel / usage export |
| Coordination | Rework cycles | Mean and max `cycle` per story | verdict markers |
| | Handoffs per story | Briefs issued by the PM | PM log / verdicts |
| | Blocked and escalated stories | Stories with `BLOCKED` or `ESCALATED` | verdict markers |
| Delivery | Deployment frequency | Production releases per week | releases |
| | Change failure rate | Production bugs / production releases | bugs + releases |
| Reliability | Failed workflow runs | Agent crash, turn cap, or session loss requiring a restart | PM escalations, CI |
| | Recovery success | Restarts that completed without human help | same |
| Human involvement | Interventions per story | PO actions beyond the fixed gates (answers, fixes, overrides) | escalation replies |
| | Approval latency | Time stories sit in `ready-for-release` | labels / PRs |

Run `python3 scripts/metrics.py --since <date>` weekly. Include the summary in the PM's
weekly planning comment.

## Instrumentation

1. **Verdict markers** (already required) carry `story`, `agent`, `verdict`, `sha`, `cycle`, and
   optionally `cost_usd`.
2. **Usage and cost:** use one API key (or Console workspace) per project and configuration
   so Console usage reports give cost per experiment. For finer detail, enable Claude Code
   OpenTelemetry export (`CLAUDE_CODE_ENABLE_TELEMETRY=1` plus an OTLP exporter) in the
   environment or user settings. Telemetry variables in a project's `.claude/settings.json` are
   ignored by design.
3. **Bug intake:** every bug uses the bug form, so "where it was found" is recorded and escaped
   defects can be counted.

## Experiment design (milestone M3)

**Benchmark:** a reference app at a tagged commit plus a fixed **benchmark backlog of 10
stories**: 3 small, 5 medium, 2 large, including 2 risk:2 stories (auth or money math).
Each story has PO-written acceptance criteria and a **held-out test suite** that agents never
see. The held-out suite is the ground truth for escaped defects.

**Configurations:**

| ID | Team | Purpose |
|---|---|---|
| C1 | Single general-purpose coding agent (Opus), self-tests, no independent QA or review | Baseline: is the team worth it? |
| C2 | PM + 1 developer + QA + reviewer (default models) | Proposed default |
| C3 | C2 + second developer, parallel independent stories | Does parallelism pay? |
| C4 | C2 with all roles on Opus | Is model tiering a false economy? |
| C5 | C2 + cross-vendor second reviewer (for example, Codex) on risk:2 stories | Does model diversity catch more? |

**Protocol:**
1. For every run, reset to the benchmark tag and use the same backlog order, prompts and tool versions.
2. Run each configuration on all 10 stories, **3 repetitions** (agent output is
   nondeterministic). Record the configuration ID in the API key or workspace name.
3. After each run: execute the held-out suites, collect metrics, and have a human grade a random
   sample of 3 PRs per run, blinded to configuration.
4. Cap budget per run (Console spend limit) and record any runs that hit it as failures.

**Analysis:** report the median and range per configuration for quality (held-out pass rate,
escaped defects, rubric), cost per accepted story, lead time, and human interventions.

**Decision rule:** choose the configuration with the **lowest cost per accepted story** among
those whose held-out pass rate is within 5 percentage points of the best and whose escaped
defects are no worse than the best. Ties go to the smaller team. Record the decision as an ADR.

**Threats to validity:** small sample (mitigate with repetitions and a mix of story types); prompt
tuning favoring C2 (freeze prompts before M3); benchmark leakage (held-out tests stay outside
the repo); model or version drift during the experiment (pin model IDs for the M3 window).
