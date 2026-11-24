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
Rules: order by dependency; keep tasks small enough for one Builder pass; every FR/NFR/AC maps to at least one task (list any gaps explicitly); keep backend and frontend tasks separate.

Present a short summary, get user approval, then point to `/dev-harness:build-app`.
