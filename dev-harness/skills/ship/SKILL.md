---
name: ship
description: Stage 6 of dev-harness. Update docs, run final checks, review QA and audit reports, summarize changes, and commit/push only with separate explicit user approval.
disable-model-invocation: true
argument-hint: "[optional: commit message hint]"
---

# /ship — Finalize and (with approval) commit

## 1. Gate (do first; stop on any failure)
- `docs/QA_REPORT.md` and `docs/REVIEW_REPORT.md` must both exist and start with `Status: PASS`. Missing, FAIL, INCOMPLETE or unparseable → **stop**, list what is outstanding, point to `/dev-harness:build-app`. Do not offer a bypass.
- Re-run the project's test/lint/build commands now. If any fail, stop and show the real output. If source changed after the reports were written, call them stale and stop.
- Confirm the review report has no unresolved Critical/High findings.

## 2. Documentation
Inspect existing docs first; edit rather than overwrite. Update README, technical docs, setup/run instructions, `.env.example` (variable names only, never real secrets), API docs, and the changelog if the project keeps one. Keep it consistent with SPEC/PLAN.

## 3. Change summary
Run `git status` and `git diff --stat`. Warn about untracked or sensitive files (`.env`, keys). Present: what changed, which SPEC items it covers, QA/review outcome, known limitations, proposed commit message.

## 4. Approval — independent of any hook
Use AskUserQuestion, one action per question; never infer approval:
1. "Commit these changes with this message?" (Approve / Edit message / Decline)
2. Only after the commit succeeds: "Push to <remote/branch>?" (Approve / Decline). Commit approval never implies push approval.
3. Deploy/publish is outside this plugin; if requested, it needs its own explicit approval.

If declined or unanswered: make **no** git changes (doc edits remain in the working tree; say so). Stage only the intended files by name, not `git add -A`, unless the user approves the full list.
Report each action's actual result. Hooks may add their own confirmation prompt; that is expected, so do not work around it.

Include the main flowchart TD architecture diagram from docs/PLAN.md inside README.md under an ## Architecture heading