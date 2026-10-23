---
name: deliver
description: Phases 3-5 of the agentic SDLC for one story. Implement with the developer, design and run tests with QA, review with the reviewer, loop on findings, and merge it through the merge gate. Use with a story issue number in status:ready.
argument-hint: <story issue number>
disable-model-invocation: true
---

# Deliver story #$ARGUMENTS

You are acting as the **PM** (see `.claude/agents/pm.md`). Keep the PO informed with
one-line status updates. Do not write code or tests yourself.

## 0. Preconditions

- `gh issue view $ARGUMENTS`: the issue is `type:story` and `status:ready`, the acceptance criteria are
  testable, and dependencies are closed. risk:2 also needs `po:approved` and an architect design note.
  If any check fails, fix the spec or escalate.
- Derive `<slug>` (2-4 words, kebab-case). Branches: `story/$ARGUMENTS-<slug>`, `qa/$ARGUMENTS-<slug>`.
- Set the label to `status:in-progress`. Set `cycle = 1`.

## 1. Build and test design in parallel

Launch both in the same turn:
- `developer`, mode `implement`
- `qa`, mode `design-tests` (risk:0 may skip this; the developer then covers each criterion
  in its own test folders, and QA verify checks that coverage)

If either returns `BLOCKED`, answer from the spec if you can. Otherwise escalate (step 5).
If the developer disputes a QA test, decide against the acceptance criteria and route the fix
to the right agent.

## 2. CI gate

- Wait for the PR checks: `gh pr checks <pr> --watch` (or `gh pr view --json statusCheckRollup`).
- If they are red, send the failures to the developer (this does not count as a cycle).
  Get the head SHA with `gh pr view <pr> --json headRefOid`.
- Set the label to `status:in-review`.

## 3. Verify in parallel (same head SHA)

Launch both in the same turn, each given the head SHA and cycle number:
- `qa`, mode `verify`
- `reviewer`

Post each returned report verbatim as a PR comment (`gh pr comment <pr> --body-file -`).
It must start with the verdict marker. Check that both verdicts name the current head SHA.

## 4. Decide

- **QA PASS + reviewer APPROVE + CI green on the same SHA:** mark the PR ready
  (`gh pr ready <pr>`), re-check the head SHA, then merge:
  `gh pr merge <pr> --squash --delete-branch --match-head-commit <sha>`.
  Set `status:ready-for-release` on the issue (it closes via `Closes #n`). Tell the PO in one
  line, including any items the reviewer flagged for human attention. If CLAUDE.md has
  `risk2_human_merge` on and the story is risk:2, ask the PO first.
  If the merge is refused (a check went red, or the head moved), go back to step 2.
- **Otherwise:** merge all blocking findings into one numbered list. If `cycle < 3`, send
  them to the developer in mode `fix` (resume the same instance if possible), then
  `cycle += 1` and go back to step 2.
- **Cycle 3 still failing:** go to step 5.

## 5. Escalate

Set `status:blocked`. Post a PR or issue comment with the marker
`{"agent":"pm","verdict":"ESCALATED",...}`, a summary of what is failing and why, the options
(re-spec, split, architect review, accept with a follow-up), and your recommendation.
Ask the PO.

## Done

After merging, staging deploys automatically. `/release` bundles merged stories for production, which the PO approves.
