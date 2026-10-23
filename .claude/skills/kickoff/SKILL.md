---
name: kickoff
description: Phases 1-2 of the agentic SDLC. Turn a product idea into a product brief, an architecture and ADRs, and a prioritized backlog of GitHub issues ready for delivery. Use when the Product Owner hands over a new project or a major feature.
argument-hint: <product idea or feature request>
disable-model-invocation: true
---

# Kickoff: idea → approved design → ready backlog

You are acting as the **PM** (see `.claude/agents/pm.md`). Product idea: $ARGUMENTS

## 1. Clarify (human gate G1 starts)

- Restate the idea in 3-5 sentences: users, problem, outcome, constraints.
- Ask the PO only the questions whose answers change scope, risk or architecture (at most
  about 7): target users, platforms, must-have vs nice-to-have, data sensitivity (money,
  PII), integrations, budget and timeline, and the definition of a successful MVP.
- Assign the overall risk profile. Anything involving payments, money math or PII makes those
  stories risk:2.

## 2. Product brief and epics

- Create a `type:brief` issue titled `Product brief: <name>` with: problem, users and
  personas, goals and non-goals, MVP scope, success metrics, constraints, risks, and open
  questions.
- Create `type:epic` issues for each capability, linked to the brief.
- **G1:** ask the PO to approve the brief and MVP scope. Do not continue until they do.

## 3. Architecture (architect, human gate G2)

- Delegate to `architect` with a brief: project setup, the brief issue number, constraints,
  and the instruction to evaluate mature existing solutions first.
- Review the returned design for completeness: contracts exist for every epic, ADRs list
  alternatives, and the walking skeleton is defined.
- **G2:** ask the PO to review and merge the `design: ...` PR (stack, ADRs, build vs buy).

## 4. Backlog

- Create one issue per story (template: `.github/ISSUE_TEMPLATE/story.yml`) from the
  architect's breakdown. Labels: `type:story`, `risk:<t>`, `status:backlog`. Link the epic.
- Story #1 is always the **walking skeleton** (developer) plus **CI and staging** (devops).
- Order by dependency, then value, then risk reduction. Present the ordered backlog and
  ask the PO to confirm the order (weekly planning). Move the top stories to
  `status:ready` (risk:2 also needs `po:approved`).

## Output to the PO

A short summary: the brief link, design PR link, ordered backlog (number, title, risk), open
questions, and the recommended first sprint (about 1 week of stories).
