#!/usr/bin/env python3
"""dev-harness PreToolUse guard.

Reads hook JSON on stdin and prints a permission decision JSON.
Layers: (1) subagent role confinement, (2) git/deploy/destructive approval gates,
(3) ship gate on QA/review reports. /ship ALSO asks the user; this hook is defense in depth.
"""
import json
import os
import re
import sys


def emit(decision, reason):
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"[dev-harness] {reason}",
        }
    }))
    sys.exit(0)


def deny(reason):
    emit("deny", reason)


def ask(reason):
    emit("ask", reason)


try:
    data = json.load(sys.stdin)
except Exception:
    sys.stderr.write("dev-harness guard: bad stdin\n")
    sys.exit(0)

tool = data.get("tool_name") or ""
ti = data.get("tool_input") or {}
cwd = data.get("cwd") or os.getcwd()

# agent_type may be "dev-harness:builder" or "builder"; only trust our three role names.
raw_role = str(data.get("agent_type") or "").lower()
short = raw_role.split(":")[-1]
is_ours = ":" not in raw_role or raw_role.startswith("dev-harness:")
role = short if is_ours and short in ("builder", "qa-tester", "reviewer") else ""

harness_active = os.path.exists(os.path.join(cwd, "docs", "SPEC.md"))


def rel_path(fp):
    full = os.path.abspath(os.path.join(cwd, fp))
    try:
        rel = os.path.relpath(full, cwd)
    except ValueError:  # different drive on Windows
        rel = full
    return rel.replace(os.sep, "/")


# ---------- file writes ----------
if tool in ("Write", "Edit", "NotebookEdit"):
    rel = rel_path(ti.get("file_path") or ti.get("notebook_path") or "")
    if role == "reviewer" and rel != "docs/REVIEW_REPORT.md":
        deny(f"Reviewer is read-only. It may write only docs/REVIEW_REPORT.md (attempted: {rel}). Report the finding instead.")
    if role == "qa-tester":
        ok = (
            rel == "docs/QA_REPORT.md"
            or re.search(r"(^|/)(tests?|__tests__|spec|specs|e2e|cypress|playwright|qa)/", rel, re.I)
            or re.search(r"\.(test|spec)\.[a-z0-9]+$", rel, re.I)
            or re.search(r"(^|/)test_[^/]+\.py$", rel, re.I)
            or re.search(r"_test\.(go|py|rb|rs)$", rel, re.I)
            or re.search(r"(^|/)conftest\.py$", rel, re.I)
        )
        if not ok:
            deny(f"QA Tester may edit only tests and docs/QA_REPORT.md (attempted: {rel}). Report application bugs instead of fixing them.")
    if role == "builder" and rel in ("docs/SPEC.md", "docs/QA_REPORT.md", "docs/REVIEW_REPORT.md"):
        deny(f"Builder must not modify {rel}. SPEC changes need user approval via the orchestrator; reports belong to QA/Reviewer.")
    sys.exit(0)

# ---------- shell commands ----------
cmd = str(ti.get("command") or "")


def split_segments(s):
    """Quote-aware split on ; & | newline."""
    out, cur, q, i = [], "", "", 0
    while i < len(s):
        c = s[i]
        if q:
            cur += c
            if c == q:
                q = ""
            elif c == "\\" and q == '"':
                i += 1
                cur += s[i] if i < len(s) else ""
        elif c in "\"'":
            q = c
            cur += c
        elif c in ";&|\n":
            if cur.strip():
                out.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    if cur.strip():
        out.append(cur.strip())
    return out


def tokenize(seg):
    toks, cur, q, has = [], "", "", False
    for c in seg:
        if q:
            if c == q:
                q = ""
            else:
                cur += c
        elif c in "\"'":
            q = c
            has = True
        elif c.isspace():
            if cur or has:
                toks.append(cur)
            cur, has = "", False
        else:
            cur += c
    if cur or has:
        toks.append(cur)
    while toks and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]) or toks[0] in ("sudo", "env", "command", "time", "nohup")):
        toks.pop(0)
    return toks


def git_sub(t):
    """Return (subcommand, args) if t is a git invocation, else None."""
    if not t or re.sub(r"\.exe$", "", os.path.basename(t[0])) != "git":
        return None
    i = 1
    while i < len(t) and t[i].startswith("-"):
        i += 2 if t[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
    return (t[i] if i < len(t) else ""), t[i + 1:]


DEPLOY_PATTERNS = [re.compile(p) for p in (
    r"^(npm|yarn|pnpm|bun)\s+publish\b", r"^twine\s+upload\b", r"^cargo\s+publish\b",
    r"^docker\s+(push|stack\s+deploy)\b", r"^kubectl\s+(apply|delete|rollout|create|replace)\b",
    r"^helm\s+(install|upgrade|uninstall|rollback)\b", r"^terraform\s+(apply|destroy)\b",
    r"^tofu\s+(apply|destroy)\b", r"^pulumi\s+(up|destroy)\b",
    r"^vercel\b(?!\s+(dev|env|whoami|login)\b)", r"^netlify\s+deploy\b", r"^(fly|flyctl)\s+deploy\b",
    r"^firebase\s+deploy\b", r"^heroku\s+(releases|container:release)\b", r"^(serverless|sls)\s+(deploy|remove)\b",
    r"^cdk\s+(deploy|destroy)\b", r"^gcloud\b.*\b(deploy|delete)\b", r"^az\b.*\b(deploy|delete)\b",
    r"^aws\b.*\b(deploy|s3\s+(sync|cp|rm)|delete-\S+)\b", r"^gh\s+(release\s+(create|delete)|pr\s+merge|repo\s+delete)\b",
    r"^wrangler\s+(deploy|publish)\b",
)]


def is_deploy(t):
    j = " ".join(t)
    return any(p.search(j) for p in DEPLOY_PATTERNS)


def destructive(t):
    j = " ".join(t)
    if re.match(r"^rm\b", j) and re.search(r"\s-[a-zA-Z]*r", j) and re.search(r"\s-[a-zA-Z]*f", j):
        return "recursive forced delete"
    if re.match(r"^(Remove-Item|rd|rmdir|del)\b", j, re.I) and re.search(r"-Recurse", j, re.I):
        return "recursive delete"
    if re.search(r"\b(DROP\s+(TABLE|DATABASE)|TRUNCATE\s+TABLE)\b", j, re.I):
        return "destructive SQL"
    return ""


def gate_status(name):
    p = os.path.join(cwd, "docs", name)
    if not os.path.exists(p):
        return "MISSING"
    with open(p, encoding="utf-8", errors="replace") as f:
        head = "".join(f.readlines()[:25])
    m = re.search(r"^\W*status\W*[:\-]?\W*(PASS|FAIL|INCOMPLETE)\b", head, re.I | re.M)
    return m.group(1).upper() if m else "UNKNOWN"


def ship_gate():
    if not harness_active:
        return ""
    bad = []
    for f in ("QA_REPORT.md", "REVIEW_REPORT.md"):
        s = gate_status(f)
        if s != "PASS":
            bad.append(f"docs/{f}: {s}")
    if bad:
        return (f"Verification not passed ({'; '.join(bad)}). Run the QA/Reviewer stages via /build-app "
                'and resolve failures. Reports must start with "Status: PASS".')
    return ""


READONLY_GIT = {"status", "diff", "log", "show", "blame", "ls-files", "rev-parse", "grep", "shortlog",
                "describe", "ls-tree", "cat-file", "remote", "branch", "config"}
READONLY_CMDS = {"ls", "cat", "head", "tail", "wc", "grep", "rg", "find", "tree", "file", "stat", "pwd",
                 "echo", "sort", "uniq", "diff", "du", "which", "type", "dir"}
SUBAGENT_BLOCKED_GIT = {"commit", "push", "tag", "reset", "clean", "rebase", "merge", "checkout", "switch",
                        "stash", "restore", "am", "cherry-pick", "revert"}

if role == "reviewer":
    unquoted = re.sub(r"([\"'])(?:\\.|(?!\1).)*\1", "", cmd)
    if re.search(r"[<>]|`|\$\(", unquoted):
        deny("Reviewer Bash is read-only: no redirects or command substitution.")
    for seg in split_segments(cmd):
        t = tokenize(seg)
        if not t:
            continue
        g = git_sub(t)
        base = os.path.basename(t[0])
        ok = False
        if g:
            sub, args = g
            ok = sub in READONLY_GIT
            if sub == "branch" and any(re.match(r"^-(d|D|m|M|c|C)$|--delete", a) for a in args):
                ok = False
            if sub == "config" and "--get" not in args:
                ok = False
        elif base in READONLY_CMDS:
            ok = not (base == "find" and any(re.match(r"^-(delete|exec|execdir|ok|fprint)", a) for a in t))
        elif base in ("npm", "pnpm", "yarn"):
            ok = len(t) > 1 and t[1] in ("audit", "ls", "list", "outdated")
        elif base in ("pip", "pip3"):
            ok = len(t) > 1 and t[1] in ("list", "check", "show")
        elif base in ("pip-audit", "bandit", "semgrep", "gitleaks", "trivy"):
            ok = True
        if not ok:
            deny(f'Reviewer may run only read-only inspection commands (blocked: "{seg[:80]}").')
    sys.exit(0)

for seg in split_segments(cmd):
    t = tokenize(seg)
    if not t:
        continue
    g = git_sub(t)
    if g:
        sub, args = g
        joined = " ".join(args)
        force_push = sub == "push" and re.search(r"(^|\s)(-f|--force|--force-with-lease|\+\S+)(\s|$)", joined)
        if role and sub in SUBAGENT_BLOCKED_GIT:
            deny(f'Subagent "{role}" may not run "git {sub}". Version-control changes happen only in /ship after user approval.')
        if sub == "push":
            gate = ship_gate()
            if gate:
                deny(f"git push blocked. {gate}")
            ask(f"{'FORCE ' if force_push else ''}git push publishes code externally. "
                "Confirm the user explicitly approved pushing (separate from committing).")
        if sub == "commit":
            gate = ship_gate()
            if gate:
                deny(f"git commit blocked. {gate}")
            if harness_active:
                ask("Confirm the user explicitly approved this commit and its message.")
        if ((sub == "reset" and "--hard" in args)
                or (sub == "clean" and any(re.match(r"^-[a-z]*f", a) for a in args))
                or (sub == "checkout" and "--" in args and "." in args)
                or (sub == "branch" and "-D" in args)):
            ask(f'"git {sub}" can discard work irreversibly. Confirm with the user.')
        continue
    if is_deploy(t):
        if role:
            deny(f'Subagent "{role}" may not run deploy/publish commands ("{seg[:80]}").')
        ask(f'Deploy/publish/infra command ("{seg[:80]}") is externally visible. Confirm explicit user approval for this action.')
    d = destructive(t)
    if d:
        ask(f'Destructive operation ({d}): "{seg[:80]}". Confirm with the user.')
sys.exit(0)
