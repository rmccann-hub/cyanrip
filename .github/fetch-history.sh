#!/bin/sh
# Fetch exactly the history a CI job reads, by explicit refspec (PROTOCOL.md
# v9 §17, HR-2 point 8b): the commit under test with all of its history, and
# each branch named, in full. Never `fetch-depth: 0`, which fetches every
# branch and every tag, and so the evidence branch too.
#
#   .github/fetch-history.sh platterpus-fork master    # the suite's jobs
#   .github/fetch-history.sh platterpus-fork --tags    # the tag job
#   .github/fetch-history.sh ... --evidence            # the ONE job that may
#
# --evidence adds refs/heads/evidence, which exactly one job does (8a);
# tests/workflows.py counts them. Before the move there is no such branch, and
# that is said rather than failed on; any other ls-remote failure fails.
set -eu
set -f   # +refs/tags/*:refs/tags/* is a refspec, not a glob
refspecs=""
evidence=no
for a in "$@"; do
    case "$a" in
        --evidence) evidence=yes ;;
        --tags) refspecs="$refspecs +refs/tags/*:refs/tags/*" ;;
        *) refspecs="$refspecs +refs/heads/$a:refs/remotes/origin/$a" ;;
    esac
done
if [ "$evidence" = yes ]; then
    set +e
    git ls-remote --exit-code origin refs/heads/evidence >/dev/null
    rc=$?
    set -e
    case $rc in
        0) refspecs="$refspecs +refs/heads/evidence:refs/remotes/origin/evidence" ;;
        2) echo "origin has no evidence branch yet: run evidence is still on" \
                "the default branch, and nothing more is fetched for it" ;;
        *) echo "git ls-remote failed ($rc): cannot tell whether origin has" \
                "an evidence branch" >&2
           exit "$rc" ;;
    esac
fi
deepen=""
if [ "$(git rev-parse --is-shallow-repository)" = true ]; then
    deepen=--unshallow
fi
# Split on purpose: each refspec is one word, and none holds a space.
# shellcheck disable=SC2086
git fetch --no-tags --prune $deepen origin "$GITHUB_SHA" $refspecs
echo "fetched $GITHUB_SHA with its history, and:$refspecs"
