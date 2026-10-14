#!/bin/sh
# HR-2 (PROTOCOL.md v9 §17), point 7: keep the evidence branch out of every
# later fetch of this clone. It cannot change the clone the session was made
# from, so it shrinks the checkout's future, not the first download. An
# explicit refspec still fetches the branch; tools/evidence.py fetches into a
# separate repository anyway. CLAUDE.md carries the same lines for a session
# where hooks do not run. Never fails the session: it says what it did.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
# A negative refspec needs git 2.29 or later.
set -- $(git version | sed -n 's/^git version \([0-9]*\)\.\([0-9]*\).*/\1 \2/p')
if [ "${1:-0}" -lt 2 ] || { [ "${1:-0}" -eq 2 ] && [ "${2:-0}" -lt 29 ]; }; then
    echo "evidence: git $(git version) has no negative refspecs, so the" \
         "evidence branch is not excluded from fetches"
    exit 0
fi
for r in $(git remote); do
    if ! git config --get-all "remote.$r.fetch" | grep -qx '\^refs/heads/evidence'; then
        git config --add "remote.$r.fetch" '^refs/heads/evidence'
        echo "evidence: remote $r no longer fetches refs/heads/evidence"
    fi
done
exit 0
