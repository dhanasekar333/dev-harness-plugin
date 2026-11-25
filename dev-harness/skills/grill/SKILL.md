---
name: grill
description: Stage 1 of dev-harness. Interview the user about a project (new or existing) until requirements are clear, then write docs/SPEC.md. Does not plan or implement.
disable-model-invocation: true
argument-hint: "[short project idea or path to brief]"
---

# /grill — Discover requirements

Goal: produce an approved `docs/SPEC.md`. **Do not plan or write application code.**

## Setup
1. Inspect the workspace (README, manifests, `docs/`, source layout). If code exists, treat this as an existing project: learn the stack and conventions first and ask only what you cannot infer.
2. If `docs/SPEC.md` exists, read it and ask whether to refine or replace it. Never overwrite without confirmation.
3. Use `$ARGUMENTS` (idea or brief path) as the starting point.

## Interview rules
- Ask in small batches (1–3 related questions; AskUserQuestion when options are enumerable, plain text otherwise). Adapt each batch to prior answers.
- Target roughly 15–30 questions total; stop earlier once the checklist is satisfied. Never pad.
- Challenge vague answers ("fast", "secure", "simple") and ask for a measurable form. Surface contradictions and missing requirements yourself.
- When the user is unsure, offer a recommended default and record it as an explicit assumption.
- Track internally: Confirmed / Assumed / Open.

## Coverage checklist
Business goal and success metrics · users and roles · core features and workflows · UI/UX (screens, accessibility, responsiveness) · tech stack and constraints · APIs and contracts · data model and database · integrations · auth and security/privacy · error and edge cases · performance/scale · deployment/environments · out of scope · acceptance criteria.

## Output: `docs/SPEC.md`
Summarize the spec and get explicit user approval before writing. Use stable IDs; later stages trace to them:

```
# SPEC: <name>
Status: APPROVED   (date)
## 1. Goals & Success Metrics
## 2. Users & Roles
## 3. Functional Requirements      — FR-1, FR-2 … (each testable)
## 4. Non-Functional Requirements  — NFR-1 … (measurable)
## 5. UI/UX
## 6. Architecture & Stack Constraints
## 7. APIs & Data
## 8. Integrations
## 9. Security & Privacy
## 10. Edge Cases & Error Handling
## 11. Acceptance Criteria         — AC-1 … (each maps to FR/NFR ids)
## 12. Out of Scope
## 13. Assumptions & Open Questions
## 14. Change Log
```

Unresolved items go under section 13, never silently decided. End by telling the user to run `/dev-harness:plan-app`.

After the user confirms docs/SPEC.md, immediately invoke the dev-harness:plan-app skill.