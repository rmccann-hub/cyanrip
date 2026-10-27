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
v=$(git version | sed -n 's/^git version \([0-9]*\)\.\([0-9]*\).*/\1 \2/p')
major=${v%% *} minor=${v#* }
if [ "${major:-0}" -lt 2 ] || { [ "${major:-0}" -eq 2 ] && [ "${minor:-0}" -lt 29 ]; }; then
    echo "evidence: git $(git version) has no negative refspecs, so the" \
         "evidence branch is not excluded from fetches"
    exit 0
fi
for r in $(git remote); do
    if ! git config --get-all "remote.$r.fetch" | grep -qx '\^refs/heads/evidence'; then
        # Said only once git has written it (review C item 4.7): a locked
        # or unwritable config leaves the branch in every fetch
        if git config --add "remote.$r.fetch" '^refs/heads/evidence'; then
            echo "evidence: remote $r no longer fetches refs/heads/evidence"
        else
            echo "evidence: remote $r still fetches refs/heads/evidence:" \
                 "git config could not add the exclusion"
        fi
    fi
done
exit 0
