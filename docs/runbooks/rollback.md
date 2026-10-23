# Runbook: rollback

**Who:** a human (PO or on-call) executes; devops prepares. **Goal:** restore the last known-good
release first, investigate second.

1. **Detect:** a smoke test failed in the deploy workflow, an alert fired, or there is a user report.
   Open a `type:bug` issue ("Where it was found: production") and note the time.
2. **Decide (≤ 10 min):** if users are affected and the cause is not obvious, roll back.
3. **Roll back production:** in GitHub, open Actions → Deploy → the run for the **previous**
   release tag and choose *Re-run jobs*, or re-publish the previous release. Approve the
   `production` environment. Database migrations must be backward-compatible (expand/contract)
   so that the previous release runs on the current schema. If one is not, follow its documented down-migration.
4. **Verify:** smoke tests pass; error rate and latency are back to baseline.
5. **Fix forward:** the PM creates a story (risk tier per impact) with a regression test; it flows
   through `/deliver` like any other change.
6. **Learn:** a short note on the bug issue covering the cause, why gates missed it, and which gate or test was added.

Projects should replace step 3 with their concrete commands (`make rollback-production TAG=...`).
