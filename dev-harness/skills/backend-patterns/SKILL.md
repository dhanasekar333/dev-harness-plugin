---
name: backend-patterns
description: Framework-agnostic backend engineering patterns (layering, API contracts, validation, auth, data access, errors, observability, security). Use when implementing or reviewing server-side code.
---

# Backend patterns

Apply only what fits the project's approved stack (see `docs/PLAN.md`). Existing conventions override these defaults. Extend by adding files under `references/` (e.g. `references/postgres.md`) and linking them here.

## Structure
- Layers: transport (routes/controllers) → service/domain logic → data access. No business logic in handlers; no transport types in the domain.
- Configuration via environment; no hard-coded secrets or URLs; provide `.env.example` with names only.
- Dependency injection (or equivalent) at boundaries so logic is testable.

## API contracts
Implement exactly the contracts in PLAN.md. Consistent resource naming, status codes, and error envelope (stable `code`, human `message`, no internals). Version breaking changes. Paginate list endpoints. Make unsafe retries safe with idempotency keys where relevant.

## Validation and errors
Validate and normalize all input at the boundary (type, range, size, format); reject unknown fields where appropriate. Fail with typed errors mapped centrally to responses; never leak stack traces or SQL; log with context.

## Auth and security
Authenticate at the edge and authorize per resource/action (deny by default; check ownership, not just role). Hash passwords with a modern KDF; short-lived tokens; rate-limit auth and expensive endpoints. Parameterized queries only; escape output; limit upload types/sizes; set secure headers/CORS narrowly; keep secrets out of logs.

## Data
Migrations are versioned, reversible when feasible, and never edited after merge. Use transactions for multi-step writes; add indexes for real query paths; avoid N+1; soft-delete only when SPEC requires.

## Reliability and observability
Timeouts and bounded retries on outbound calls; graceful shutdown; structured logs with request IDs; health endpoint; metrics on key paths.

## Testing
Unit-test services; integration-test endpoints and DB with real (containerized/in-memory-equivalent) dependencies; contract tests for external APIs; cover auth failures and validation errors.
