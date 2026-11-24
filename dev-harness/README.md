# dev-harness

A Claude Code plugin that runs software development as an approval-driven lifecycle: requirements interview → plan → build → QA → audit → ship. It works on new and existing projects, and never commits, pushes, or deploys without explicit user approval.

## Workflow

| Stage | Command | Output |
|---|---|---|
| 1 Discover | `/dev-harness:grill` | `docs/SPEC.md` (FR/NFR/AC ids) |
| 2 Plan | `/dev-harness:plan-app` | `docs/PLAN.md` (tasks traced to SPEC ids) |
| 3 Build | `/dev-harness:build-app` | code + ticked tasks; orchestrates stages 3–5 |
| 4 Verify | `qa-tester` subagent | `docs/QA_REPORT.md` |
| 5 Audit | `reviewer` subagent (read-only) | `docs/REVIEW_REPORT.md` |
| 6 Ship | `/dev-harness:ship` | docs updated; commit/push only on approval |

Traceability: SPEC ids → PLAN tasks (`Implements:`) → QA traceability table → review compliance table.
Report files start with `Status: PASS | FAIL | INCOMPLETE`; `/ship` and the hooks treat anything but PASS as blocking.

## Components

- `skills/` — `grill`, `plan-app`, `build-app`, `ship` (user-invoked only), plus `frontend-patterns` and `backend-patterns` (preloaded into the Builder; extend with `references/` files).
- `agents/` — `builder` (Read, Glob, Grep, Edit, Write, Bash), `qa-tester` (same tools, hook-limited to tests and its report), `reviewer` (Read, Glob, Grep, Bash, Write; hook-limited to `docs/REVIEW_REPORT.md` and read-only commands).
- `hooks/` — `PreToolUse` guard (`guard.py`, requires Python 3 on PATH as `python3` or `python`):
  - subagents cannot git commit/push or deploy; Reviewer/QA/Builder file-write confinement;
  - `git push`, deploys/publishes, force operations and recursive deletes ask for confirmation;
  - in a project with `docs/SPEC.md`, `git commit`/`push` are denied unless both reports say `Status: PASS`.

Hooks are defense in depth. `/ship` independently asks the user, separately for commit and push.

## Install

Requires Python 3 (`python3` or `python`) on PATH for the safety hook.

```text
/plugin install dev-harness --marketplace dhanasekar333/dev-harness-plugin
```
(Claude Code 2.1.275 or later.) On older versions:
```text
/plugin marketplace add dhanasekar333/dev-harness-plugin
/plugin install dev-harness@dev-harness-marketplace
```
The marketplace lives at https://github.com/dhanasekar333/dev-harness-plugin.

## Local testing

```bash
claude plugin validate ./dev-harness
claude --plugin-dir ./dev-harness     # load for one session; /reload-plugins after edits
```

## Example session

```text
/dev-harness:grill a booking app for dental clinics
/dev-harness:plan-app
/dev-harness:build-app            # or: /dev-harness:build-app T1-T4
/dev-harness:ship
```

## Notes and limits

- Plugin agents ignore `hooks`, `permissionMode` and `mcpServers` frontmatter, so role confinement lives in the plugin-level hook, keyed on `agent_type`. Verify it in your build by running a subagent and checking that a Reviewer write outside `docs/REVIEW_REPORT.md` is denied.
- Shell parsing in the guard is best-effort; unusual command wrapping may evade the git/deploy patterns. Keep Claude Code's own permission prompts enabled.
- Report staleness is checked by `/ship` (instruction-level), not by the hook.
