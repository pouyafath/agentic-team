---
name: board
description: Show the current state of the agentic team's backlog and work in progress from GitHub, including blocked items, items waiting on the Product Owner, and the next recommended action. Use at the start of a session to resume work, or whenever the PO asks for status.
disable-model-invocation: true
---

# Board

Rebuild the state from GitHub. It is the system of record, so a new session can always resume from it.

1. `gh issue list --state open --label type:story --limit 200 --json number,title,labels,assignees,updatedAt`
2. `gh pr list --state open --json number,title,headRefName,headRefOid,isDraft,statusCheckRollup,reviewDecision`
3. For each in-review PR, read the latest verdict markers (`gh pr view <n> --json comments`)
   and check whether they name the current head SHA.

Report as a compact table per status column (Backlog, Ready, In Progress, In Review,
Ready for Release, Blocked), then:
- **Waiting on PO:** merges, approvals, escalations (with links).
- **Stale:** items with no update in more than 2 days, or verdicts on an outdated SHA.
- **Next action:** the single most valuable thing to do next, and offer to do it.

For metrics, run `python3 scripts/metrics.py` (see docs/06-evaluation.md).
