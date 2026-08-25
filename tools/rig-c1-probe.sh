#!/bin/sh
# This file is part of cyanrip.
#
# cyanrip is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# cyanrip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with cyanrip; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# =============================================================================
# C1 PROBE -- the thirty-minute hang, bounded to about two minutes
# =============================================================================
#
#   Run it:   sh tools/rig-c1-probe.sh
#   Costs:    at most ~2 minutes and 10 seconds. NO RIP. Nothing is written to
#             your music library and no audio is read.
#   Needs:    a real CD drive with ANY ordinary audio CD in it. The disc is
#             never ripped -- cyanrip reads the TOC, refuses for want of a read
#             offset, and that refusal is the whole experiment.
#
# NOTHING IN THIS FILE NEEDS EDITING.
#
# -----------------------------------------------------------------------------
# WHAT IT IS MEASURING, AND WHY IT CANNOT BE MEASURED HERE
# -----------------------------------------------------------------------------
# On the 2026-08-25 rig session, step 5b ran cyanrip with no `-s`. It hit the
# offset refusal, wrote its `-j` diagnostics record from `atexit` FOURTEEN
# SECONDS in -- so the process decided to fail and ran its exit path all the way
# to completion -- and then stayed alive for roughly THIRTY MORE MINUTES with
# the drive held, needing SIGKILL.
#
# We cannot reproduce it. The refusal is gated on `CDIO_DRIVE_CAP_READ_ISRC`, a
# DRIVE CAPABILITY that image drivers do not report, so the entire branch is
# unreachable from every disc-image fixture either project has. It needs a
# drive, and this script is the smallest thing that puts one in that state.
#
# Two of the three observations from that session are already explained, and
# NEITHER of them is the defect:
#
#   * "SIGTERM did not land" is our documented behaviour. cyanrip has caught
#     SIGTERM since +platterpus.7 -- the handler sets a flag and returns -- and
#     once the rip loop is behind it, nothing reads that flag again. A single
#     SIGTERM has not been able to terminate cyanrip since that release. That is
#     an unstated cost of a fix Platterpus asked us for, not evidence about
#     whether anything was wedged.
#
#   * The 0-byte stdout capture measured the capture, not cyanrip. A message in
#     the `-j` record is proof it reached fd 1 and was flushed -- one call site,
#     `crip_diag_record()` at the top of `cyanrip_vlog()`, which ends
#     `vprintf` + `fflush(stdout)` unconditionally. The record held four
#     messages, 174 bytes, and the capture file's own mtime never moved off the
#     second the step began.
#
# THE THIRTY MINUTES IS WHAT REMAINS, and it is ours.
#
# -----------------------------------------------------------------------------
# WHY THE CAPTURE HERE IS A PLAIN SHELL REDIRECT
# -----------------------------------------------------------------------------
# Deliberately, and it is the one design decision in this file. The open
# question is partly "does a capture retain what cyanrip writes", so the capture
# must not be the thing under suspicion. There is no pipe, no `tee`, no
# timestamper, nothing between cyanrip's fd 1 and a file on disk. When we want
# to know WHEN bytes arrived, the watcher below samples the file's SIZE from
# outside rather than inserting itself into the path.
#
# ONE THING THAT IS NOT UNDER OUR CONTROL, and it is why this script now names
# what it watched. Platterpus's round-14 lap 12 §E2 records that on their rig
# `~/.local/bin/cyanrip` is a host-exported Distrobox wrapper and the real
# ripper runs in a container, so there is a container runtime forwarding stdio
# between cyanrip's fd 1 and any redirect on the host. "A plain shell redirect"
# is still the simplest capture available; it is not the same as "nothing in
# the path". If this probe comes back with an empty capture on that rig, that
# is a fact about the forwarding, not about cyanrip -- and the process-tree
# block below is what lets a reader tell.
#
# -----------------------------------------------------------------------------
# WHAT A RESULT LOOKS LIKE -- all four are results, none is a failure
# -----------------------------------------------------------------------------
#   A. Exits ~14 s, capture holds the four messages.  The hang did not
#      reproduce. Still worth having: it says the capture path is fine and the
#      hang is intermittent or was specific to that session.
#   B. Exits ~14 s, capture is EMPTY.  Then the emptiness is reproducible and
#      belongs to the harness, exactly as lap 11 §C argues.
#   C. Hangs past 20 s.  Then `wchan` in the sample block names the kernel
#      function it is parked in, and that one word ends the question.
#   D. Refuses before reaching any of the above -- no drive, no disc, drive
#      reports no ISRC capability.  A real result about the rig, not a failure
#      of the probe. The summary says which.
#
# Send back the whole output directory. It is a few kilobytes.
# =============================================================================

set -u

BUDGET=120          # seconds before SIGTERM
GRACE=5             # seconds after that before SIGKILL
SAMPLE_EVERY=5      # seconds between /proc samples
EXPECT_BY=20        # the run should be over well before this; past it is case C

CRIP=${1:-}
DEV=${2:-}          # optional; omitted means "let cyanrip find the drive"
if [ -z "$CRIP" ]; then
    CRIP=$(command -v cyanrip 2>/dev/null || true)
fi
if [ -z "$CRIP" ] || [ ! -x "$CRIP" ]; then
    echo "cannot find a cyanrip binary. Pass its path, and optionally a device:" >&2
    echo "    sh tools/rig-c1-probe.sh /home/rmccann/.local/bin/cyanrip" >&2
    echo "    sh tools/rig-c1-probe.sh /home/rmccann/.local/bin/cyanrip /dev/cdrom" >&2
    exit 2
fi

STAMP=$(date -u +%Y%m%d-%H%M%S)
OUT="c1-probe-$STAMP"
mkdir -p "$OUT/scratch" || exit 2
SUM="$OUT/00-summary.txt"

say() { echo "$@" | tee -a "$SUM"; }

say "=== C1 probe $STAMP (UTC)"
say "    binary:  $CRIP"
say "    budget:  ${BUDGET}s then SIGTERM, +${GRACE}s then SIGKILL"
say "    expect:  a refusal in about 14 seconds"
say ""

"$CRIP" --version > "$OUT/01-version.txt" 2>&1
say "--- cyanrip --version"
sed 's/^/    /' "$OUT/01-version.txt" | tee -a "$SUM"
say ""

RAW="$OUT/02-stdout-raw.txt"
DIAG="$OUT/scratch/diag.json"

# Created here so its birth time is on the record, exactly as the rig harness's
# 05-minus-j.txt was. If it ends the run at this size and this mtime, that is
# case B and it is the same measurement as the one in lap 11 §C.
: > "$RAW"
say "--- capture file created"
say "    $(ls -l --time-style=+%Y-%m-%dT%H:%M:%S "$RAW" 2>/dev/null || ls -l "$RAW")"
say ""

T0=$(date -u +%s)
say "--- launching at epoch $T0"
say "    argv: timeout -k $GRACE $BUDGET $CRIP${DEV:+ -d $DEV} -j $DIAG -D $OUT/scratch -o flac -N -l 1 -u platterpus/c1-probe"
say ""

# No pipe. A plain redirect, for the reason in the header above.
#
# -d is unquoted-empty-safe only because it is guarded: an empty "-d ''" would
# be a device named "", not an absent flag, and cyanrip would refuse on it.
if [ -n "$DEV" ]; then
    timeout -k "$GRACE" "$BUDGET" "$CRIP" -d "$DEV" \
        -j "$DIAG" -D "$OUT/scratch" -o flac -N -l 1 -u platterpus/c1-probe \
        > "$RAW" 2>&1 &
else
    timeout -k "$GRACE" "$BUDGET" "$CRIP" \
        -j "$DIAG" -D "$OUT/scratch" -o flac -N -l 1 -u platterpus/c1-probe \
        > "$RAW" 2>&1 &
fi
SHELL_PID=$!

# The pid we want is cyanrip's, not `timeout`'s. Resolve it from timeout's
# children rather than assuming, because /proc/<timeout>/wchan would report on
# the wrong process and would look like a perfectly good answer.
# Every descendant of $1, depth first. Recursive on purpose: on the rig the
# binary at $CRIP is NOT cyanrip.
#
# THE DEFECT THIS REPLACES, and it was in the first version of this script.
# It took the LAST DIRECT CHILD of `timeout` and called it "cyanrip pid". That
# is right only when the thing you exec IS the thing you want to watch.
# Platterpus's round-14 lap 12 §E2 told us it is not: their `$RIPPER`,
# `~/.local/bin/cyanrip`, is a host-exported Distrobox wrapper and the real
# ripper runs inside a container. So the pid we would have sampled is a
# launcher, `wchan` would have named whatever a launcher waits on, and it would
# have looked like a perfectly good answer.
#
# That is the exact trap this script's own header claimed to have avoided --
# "resolves the pid from timeout's children rather than assuming, because wchan
# on the wrong process would look like a perfectly good answer". We wrote the
# warning and then shipped the bug, because we tested against a bare binary. It
# needed a fact about somebody else's rig that we could not have derived.
descendants() {
    for c in $(cat "/proc/$1/task/$1/children" 2>/dev/null); do
        echo "$c"
        descendants "$c"
    done
}
comm_of() { cat "/proc/$1/comm" 2>/dev/null; }

CRIP_PID=""
PID_SOURCE=""
i=0
while [ "$i" -lt 60 ]; do
    TREE=$(descendants "$SHELL_PID")
    for c in $TREE; do
        if [ "$(comm_of "$c")" = "cyanrip" ]; then
            CRIP_PID=$c
            PID_SOURCE="a descendant of timeout, comm=cyanrip"
        fi
    done
    [ -n "$CRIP_PID" ] && break
    kill -0 "$SHELL_PID" 2>/dev/null || break   # already over; nothing to sample
    i=$((i + 1))
    sleep 0.25
done

# Not a descendant we can see? It may still be visible in the host's /proc --
# a container sharing the host PID namespace puts it there without making it a
# child of anything we launched. We do NOT assume either way: that is a fact
# about a runtime we have not read.
#
# A unique match is used and LABELLED as coming from outside the tree. Two or
# more is refused rather than picked from, because guessing which cyanrip is
# ours would produce a wchan line indistinguishable from a correct one.
if [ -z "$CRIP_PID" ] && kill -0 "$SHELL_PID" 2>/dev/null; then
    HITS=$(pgrep -x cyanrip 2>/dev/null | tr '\n' ' ')
    NHITS=$(printf '%s' "$HITS" | wc -w | tr -d ' ')
    if [ "$NHITS" = "1" ]; then
        CRIP_PID=$(printf '%s' "$HITS" | tr -d ' ')
        PID_SOURCE="pgrep -x cyanrip -- NOT a descendant of timeout, so this \
process was found in the host's /proc without being a child of anything we \
launched"
    elif [ "$NHITS" != "0" ]; then
        say "--- pgrep found $NHITS processes named cyanrip. REFUSING to pick"
        say "    one: the wrong one produces a wchan line that looks correct."
    fi
fi

# The tree goes in the record either way. It costs nothing and it is the thing
# that explains an empty sample block to whoever reads the bundle.
say "--- process tree under timeout $SHELL_PID"
TREE=$(descendants "$SHELL_PID")
if [ -z "$TREE" ]; then
    say "    (none -- already exited, or children are not visible here)"
else
    for c in $TREE; do
        say "    pid $c  comm=$(comm_of "$c")  exe=$(readlink "/proc/$c/exe" 2>/dev/null)"
    done
fi
say ""

if [ -n "$CRIP_PID" ]; then
    say "--- watching pid $CRIP_PID ($PID_SOURCE)"
elif ! kill -0 "$SHELL_PID" 2>/dev/null; then
    # Not a gap. The run was over before there was anything to sample, which
    # only happens when it refused long before the 14 seconds we expect.
    say "--- the run finished before a pid could be sampled, so it lasted well"
    say "    under a second. /proc samples are empty BECAUSE nothing hung."
else
    say "--- NO PROCESS NAMED cyanrip FOUND, and /proc samples are SKIPPED."
    say ""
    say "    This is a GAP, not a result, and it is deliberately not filled by"
    say "    sampling whatever we did find. If \$CRIP is a wrapper -- a"
    say "    container launcher, a shim -- then the tree above names it, and"
    say "    its wchan would describe the launcher rather than the ripper."
    say ""
    say "    If the ripper runs in a container, run this probe INSIDE it, or"
    say "    point \$CRIP at the real binary:"
    say "        distrobox enter <container> -- sh rig-c1-probe.sh /usr/local/bin/cyanrip"
fi
say ""

SAMPLES="$OUT/03-proc-samples.txt"
: > "$SAMPLES"

sample() {
    now=$(date -u +%s)
    {
        echo "=== +$((now - T0))s  (epoch $now)"
        echo "    capture bytes : $(wc -c < "$RAW" 2>/dev/null || echo '?')"
        echo "    capture mtime : $(date -u -r "$RAW" +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo '?')"
        if [ -n "$CRIP_PID" ] && [ -d "/proc/$CRIP_PID" ]; then
            echo "    state         : $(awk '/^State:/{print $2, $3}' "/proc/$CRIP_PID/status" 2>/dev/null)"
            echo "    wchan         : $(cat "/proc/$CRIP_PID/wchan" 2>/dev/null; echo)"
            for t in /proc/"$CRIP_PID"/task/*; do
                [ -d "$t" ] || continue
                echo "    thread $(basename "$t") : $(cat "$t/wchan" 2>/dev/null; echo) \
[$(awk '/^State:/{print $2}' "$t/status" 2>/dev/null)]"
            done
        elif [ -z "$CRIP_PID" ]; then
            echo "    process       : NOT IDENTIFIED -- samples skipped rather"
            echo "                    than taken from the wrong process"
        else
            echo "    process       : gone"
        fi
    } >> "$SAMPLES"
}

sample
while kill -0 "$SHELL_PID" 2>/dev/null; do
    sleep "$SAMPLE_EVERY"
    sample
done

wait "$SHELL_PID"
RC=$?
T1=$(date -u +%s)
ELAPSED=$((T1 - T0))

say "--- finished after ${ELAPSED}s, exit $RC"
say ""

BYTES=$(wc -c < "$RAW" 2>/dev/null || echo 0)
say "--- results"
say "    elapsed              : ${ELAPSED}s"
say "    exit code            : $RC"
say "                           1   = cyanrip's own refusal, which is expected"
say "                           124 = timeout fired; 137 = killed by SIGKILL."
say "                           Both mean it outlived the budget. Remember a"
say "                           single SIGTERM cannot stop cyanrip, so it is"
say "                           the -k SIGKILL that ends it either way."
say "    stdout capture bytes : $BYTES"
say "    capture mtime        : $(date -u -r "$RAW" +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo '?')"
if [ -f "$DIAG" ]; then
    say "    -j record            : written, $(wc -c < "$DIAG") bytes,"
    say "                           mtime $(date -u -r "$DIAG" +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo '?')"
else
    say "    -j record            : NOT WRITTEN -- the exit path did not complete"
fi
say ""

# A verdict about which of the four cases this is, and nothing about quality.
# Every branch is a result; the script never says "pass" or "fail".
#
# D is decided FIRST and it is not a fifth outcome bolted on: if the run never
# reached the offset refusal, it never entered the branch under investigation,
# and calling that "the hang did not reproduce" would be the same defect this
# whole round is about -- an absence read as evidence when the channel was never
# in a state to produce a presence.
REACHED=no
grep -q "Offset is unset" "$RAW" 2>/dev/null && REACHED=yes

if [ "$REACHED" = no ] && [ "$ELAPSED" -lt "$EXPECT_BY" ]; then
    say "    CASE D -- the run never reached the offset refusal, so it never"
    say "              entered the branch under investigation. This says"
    say "              NOTHING about the hang either way."
    if grep -q "No device specified" "$RAW" 2>/dev/null; then
        say "              Cause: no drive was found. Pass one explicitly:"
        say "                  sh rig-c1-probe.sh $CRIP /dev/cdrom"
    else
        say "              Check a disc is loaded and that the drive reports"
        say "              ISRC capability -- the refusal is gated on it."
    fi
elif [ "$ELAPSED" -ge "$EXPECT_BY" ]; then
    say "    CASE C -- it hung. Read the wchan lines in 03-proc-samples.txt;"
    say "              that is the measurement this probe exists for."
    [ "$REACHED" = no ] && \
        say "              (and the refusal is NOT in the capture, so read C"
    [ "$REACHED" = no ] && \
        say "               together with the CASE B question below)"
elif [ "$BYTES" -eq 0 ]; then
    say "    CASE B -- exited promptly and the capture is EMPTY. A plain shell"
    say "              redirect received nothing, which is a finding about the"
    say "              capture path and reproduces the rig's 05-minus-j.txt."
else
    say "    CASE A -- reached the refusal, exited promptly, and the capture"
    say "              holds its output. The hang did not reproduce. Still a"
    say "              result: the capture path is sound and the hang is not"
    say "              unconditional."
fi
say ""
say "--- captured stdout, verbatim"
if [ "$BYTES" -eq 0 ]; then
    say "    (empty -- 0 bytes)"
else
    sed 's/^/    /' "$RAW" | tee -a "$SUM"
fi

say ""
say "=== send back the directory: $OUT"

if command -v tar >/dev/null 2>&1; then
    tar czf "$OUT.tar.gz" "$OUT" 2>/dev/null && \
        echo "    also packaged: $OUT.tar.gz"
fi

exit 0
