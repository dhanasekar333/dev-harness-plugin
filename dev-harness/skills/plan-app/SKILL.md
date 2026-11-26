---
name: plan-app
description: Stage 2 of dev-harness. Read docs/SPEC.md and produce an architecture and ordered task plan in docs/PLAN.md. Does not implement.
disable-model-invocation: true
---

# /plan-app — Plan

Goal: write `docs/PLAN.md` from `docs/SPEC.md`. **Do not implement features or edit application code.**

## Preconditions
- `docs/SPEC.md` must exist with `Status: APPROVED`. Otherwise stop and direct the user to `/dev-harness:grill`.
- If `docs/PLAN.md` exists, read it and ask before replacing.
- Existing project: inspect the codebase first; plan changes that fit current conventions (reuse, don't rewrite).
- If SPEC open questions block design, ask the user; do not guess.

## Design content
Architecture overview · components and responsibilities · data flow · API contracts (endpoints, request/response, errors) · database schema and migrations · dependencies (with justification) · security considerations (authn/z, input validation, secrets, data protection) · testing strategy · risks.

## Output: `docs/PLAN.md`
```
# PLAN: <name>
Status: READY   Source: docs/SPEC.md
## Architecture  (components, data flow, API, schema, dependencies, security)
## Traceability matrix   FR/NFR/AC id → task ids
## Backend tasks
## Frontend tasks
## Cross-cutting tasks (setup, CI, docs)
## Risks & open questions
```
Each task is a checkbox line plus fields:
```
- [ ] T3 <title>
  Area: backend|frontend|shared   Depends: T1,T2   Implements: FR-2, AC-4
  Acceptance: <observable, testable criteria>
  Patterns: backend-patterns | frontend-patterns
```
Rules: order by dependency; keep tasks small enough for one Builder pass; keep backend and frontend tasks separate.

### Traceability matrix rules
Format: `| Req id | Build task(s) | Verification task(s) |`, one row per FR, NFR and AC.
- Every **FR** and **AC** maps to **both** its implementation task(s) AND its verification/test task(s), e.g. build `T3 (API), T6 (UI)`, verify `T7 (Browser QA), T8 (Pytest)`. This means the plan must contain explicit test tasks, so create them.
- Do not paste the same task list into every row unless tasks are strictly layer-based. If they are, still separate backend verification (e.g. `T8`) from UI verification (e.g. `T7`) for every user-facing FR.
- Derive each row from the task's `Implements:` field and the requirement's actual content; a row that does not match what the task does is wrong.
- Write "No gaps" only if every FR and AC has at least one build task and one test task. Otherwise list each gap by id.

**Self-check before presenting the plan** (this is where past matrices went wrong): re-read the finished matrix against the task list. Confirm every id in SPEC appears as a row, every task id cited exists, every cited task really lists that requirement in `Implements:`, and every FR/AC has a build and a test task. Fix the matrix, then present.

Present a short summary, get user approval, then point to `/dev-harness:build-app`.

After the user approves docs/PLAN.md, immediately invoke the dev-harness:build-app skill.

Load and follow dev-harness:mermaid-diagrams to include a flowchart TD architecture diagram, erDiagram database schema, and sequenceDiagram in docs/PLAN.md.