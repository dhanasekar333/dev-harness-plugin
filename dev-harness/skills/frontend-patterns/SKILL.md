---
name: frontend-patterns
description: Framework-agnostic frontend engineering patterns (component design, state, accessibility, forms, error/loading states, performance, security). Use when implementing or reviewing UI code.
---

# Frontend patterns

Apply only what fits the project's approved stack (see `docs/PLAN.md`). Existing project conventions override these defaults. Extend by adding files under `references/` (e.g. `references/react.md`) and linking them here.

## Structure
- Small, single-purpose components; separate presentation from data fetching and business logic.
- Colocate component, styles, and tests; share primitives through one design-system layer, not copies.
- Keep state at the lowest level that needs it; derive values instead of duplicating state; use server/cache state tools for remote data when the stack has them.

## Every screen handles
Loading, empty, error, and success states; offline/slow network; permission-denied; long/odd content (i18n, overflow).

## Forms and input
Validate client-side for UX and never rely on it for security; show field-level errors accessibly; disable double-submit; preserve user input on failure.

## Accessibility (baseline)
Semantic elements first, ARIA only to fill gaps; full keyboard operation and visible focus; labels for all inputs; sufficient contrast; announce async changes; respect reduced-motion.

## Responsiveness and performance
Mobile-first layouts; avoid layout shift; lazy-load heavy routes/assets; memoize only after measuring; optimize images; keep bundles lean.

## Security
Never inject unsanitized HTML; no secrets in client code; store tokens per the planned auth design (prefer httpOnly cookies); encode data rendered in URLs/attributes; honor CSP.

## API integration
One typed client module per backend; map errors to user-facing messages; handle cancellation and retries deliberately; match contracts in PLAN.md exactly.

## Testing
Test behavior through the user's view (roles/labels), cover state variants above, and mock only at the network boundary.
