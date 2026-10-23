---
name: release
description: Phase 6 of the agentic SDLC. Verify merged work on staging, prepare a production release with checklist and rollback plan, and hand it to the Product Owner for approval. Use after one or more stories are merged to main.
argument-hint: "[version, e.g. v0.3.0]"
disable-model-invocation: true
---

# Release $ARGUMENTS

You are acting as the **PM**. Production is a human decision (gate G4).

1. List the merged `status:ready-for-release` stories since the last release tag
   (`gh pr list --state merged --search "merged:>=<last tag date>"`).
2. Delegate to `devops` (mode: release preparation) with the version, the story list, and
   the main SHA. It must return `RELEASE_READY` with a checklist: CI green on that SHA,
   staging deployed at that SHA, smoke tests pass, monitoring live, rollback documented,
   and a draft release with notes.
3. If staging or the smoke tests fail: open `type:bug` issues for the regressions (the
   offending story goes back to `status:in-progress`) and stop the release.
4. Ask the PO to approve the `production` environment deployment in GitHub Actions and to
   publish the draft release. Include the checklist, the change summary, risk notes
   (especially risk:2 items), and the rollback command or procedure.
5. After the PO confirms the production deploy: close the released stories, and post a short
   release summary on the brief issue with the version, stories, and anything to watch.

Never deploy to production, publish the release, or change secrets yourself.
