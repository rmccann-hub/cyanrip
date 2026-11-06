#!/usr/bin/env bash
# drivetest.sh -- round 38's drive test, run by a script, on the releases
# installed now: Platterpus 0.7.121 and cyanrip 0.9.4-rc3+platterpus.30.
#
# Everything lives in ONE folder, ~/platterpus-rig/drivetest-r38/, beside the
# app's own acceptance-run folders. Three pastes in all:
#
#   bash ~/platterpus-rig/drivetest.sh 1
#        Disc in, Platterpus closed. Reads the drive, runs the two-read check
#        and the C2 probe, then Run A. Then it OPENS THE TRAY: wipe the disc
#        from the centre outward, put it back, and it carries on by itself
#        with Run B, Run C and the track 9 reads. (About 2.5 to 3 hours.)
#   bash ~/platterpus-rig/drivetest.sh 3
#        Back in Bazzite after Pioneer's utility set PureRead to Perfect (only
#        if the utility opened on your drive): reads, the C2 probe, Run D.
#   bash ~/platterpus-rig/drivetest.sh 4
#        Back in Bazzite after PureRead was set back: reads the drive and
#        checks, byte for byte, that it went back.
#
# Each ends by printing UPLOAD THIS ONE FILE: send that one file to both
# sessions. A failure is written down with its full output; the test keeps
# going when the rest still means something and stops when it would not. Run
# the same command again after a stop: finished steps are skipped. Phase 4,
# the Full acceptance run, stays the app's menu.
#
#   note TEXT   add a line to the timeline (the cloth, the room, anything)
#   redo STEP   run a finished step again next time
#   send        make an upload file from whatever exists now
#
# Every command this sends to the drive is a read. Nothing changes the drive's
# settings or firmware, and nothing is burned. Nothing is deleted: earlier
# test files are MOVED into the folder (earlier/), and the list of what you
# may delete by hand afterwards is in the folder's CLEANUP.txt.
#
# Beyond the printed sheet ("Platterpus -- Round 38 Drive Test", 5 November
# 2026), whose commands it runs as written:
#   - a timeline in UTC and local time, and FAILURES.txt with full output;
#   - before every run: Platterpus closed, the drive free, the disc ready;
#   - the two-read check: one `cyanrip -I` alone, then two at once 2.4 s
#     apart, as the app started them in Run A's failure; if the pair stalls it
#     runs again under strace to name the command it stalled in;
#   - the C2 probe: READ CD asking for C2 error pointers where tracks 3 and 5
#     read wrong, and at a clean control, three reads each; the drive's
#     capabilities page says it gives none, its CD Read feature says it does;
#   - the probe guard: while the app runs, a disc read it has abandoned for a
#     newer one is stopped, so two reads never share the drive (0.7.121 left
#     one running in Run A's failure; the real fix is Platterpus's release);
#   - a run that rips nothing is retried once; after two app runs in a row
#     that rip nothing, no more app runs start, and the reads go on;
#   - the kernel's messages about the drive, in every upload.

set -u

# A stage runs for hours: keep the machine from sleeping while it does, if
# logind will hold the lock (the run itself says whether it did).
case "${1:-}" in
1|3|4)
    if [ -z "${DRIVETEST_AWAKE:-}" ] && command -v systemd-inhibit >/dev/null 2>&1 \
        && systemd-inhibit --what=sleep:idle --who=drivetest --why="drive test" --mode=block true >/dev/null 2>&1; then
        export DRIVETEST_AWAKE="held by systemd-inhibit"
        exec systemd-inhibit --what=sleep:idle --who=drivetest --why="drive test, stage $1" --mode=block bash "$0" "$@"
    fi
    ;;
esac

RIG="$HOME/platterpus-rig"
ROOT="${DRIVETEST_ROOT:-$RIG/drivetest-r38}"
TL="$ROOT/timeline.txt"
FAIL="$ROOT/FAILURES.txt"
OUT="$ROOT/app-output"
READS="$ROOT/reads"
RUNS="$ROOT/runs"
SCRIPTS="$ROOT/scripts"
DEV=/dev/sr0
BOX=ripping
CYANRIP="$HOME/.local/bin/cyanrip"
APP="${APP:-$HOME/Applications/platterpus-x86_64.AppImage}"
BUNDLES="$HOME/.local/share/platterpus/bundles"
RIG_BASE=https://raw.githubusercontent.com/rmccann-hub/Platterpus/main/src/platterpus/rig_scripts
WANT_APP="platterpus 0.7.121"
WANT_RIPPER="cyanrip 0.9.4-rc3+platterpus.30"
# The reference disc's TOC, as .30 printed it on 5 November
WANT_TOC="1+14+268857+150+14637+28217+50070+72720+90792+109325+128907+145812+159387+178482+201012+224660+246677"
CHECK_SECS="${CHECK_SECS:-150}"
WAIT_DISC_SECS="${WAIT_DISC_SECS:-14400}"
POLL_SECS="${DRIVETEST_POLL_SECS:-5}"      # how often a wait looks again
SETTLE_SECS="${DRIVETEST_SETTLE_SECS:-10}" # the sheet's wait after the disc goes back in
F4_CDB='3c 02 f4 00 00 00 00 01 00 00'
# shellcheck disable=SC2016  # expanded by the container's shell, not this one
STD_QUERIES='sg_inq /dev/sr0; sg_get_config -q /dev/sr0; sg_get_config -q -H /dev/sr0; for c in 0 1 2 3; do echo "=== page control $c ==="; sg_modes -a -c $c /dev/sr0; done'

STAGE="${1:-}"
STAGE_START_EPOCH=$(date +%s)
case "$STAGE" in
    1|3|4|note|redo|send) mkdir -p "$ROOT" "$OUT" "$READS" "$RUNS" "$SCRIPTS" ;;
esac

# ---- the timeline and the failures ------------------------------------------------

stamp() { printf '%s | %s' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(date '+%-I:%M:%S %p %Z')"; }
say()   { printf '%s | %s\n' "$(stamp)" "$*" | tee -a "$TL"; }

NFAIL=0
failed() {   # STEP WHY [FILE]
    NFAIL=$((NFAIL + 1))
    say "FAILED: $1: $2"
    {
        printf '\n=== %s | %s: %s\n' "$(stamp)" "$1" "$2"
        if [ -n "${3:-}" ] && [ -f "$3" ]; then
            printf -- '--- last 60 lines of %s (the whole file is in the upload)\n' "${3#"$HOME"/}"
            tail -n 60 "$3"
        fi
    } >> "$FAIL"
}

fresh() {   # a name not taken yet: x, then x-2, x-3, ...
    local p="$1" ext="${2:-}" n=2
    local try="$p$ext"
    while [ -e "$try" ]; do try="$p-$n$ext"; n=$((n + 1)); done
    printf '%s\n' "$try"
}

# ---- the machine's state ------------------------------------------------------------

rips_dir() {
    local r=""
    if [ -f "$HOME/.config/platterpus/config.toml" ]; then
        r="$(grep -E '^output_dir' "$HOME/.config/platterpus/config.toml" | sed -E 's/.*= *"(.*)"/\1/')"
    fi
    r="${r:-$HOME/Music/rips}"
    printf '%s\n' "${r/#\~/$HOME}"
}

# A running app: a process whose program (its first word) is the AppImage or
# lives in its mount; a shell or editor that only mentions it is not one.
app_running() {
    pgrep -f -- "^[^ ]*$(basename "$APP")" >/dev/null 2>&1 || pgrep -f '^[^ ]*/\.mount_platte' >/dev/null 2>&1
}

drive_held() { command -v fuser >/dev/null 2>&1 && fuser -s "$DEV" 2>/dev/null; }
holders()    { fuser -v "$DEV" 2>&1 | tr -s ' \n' ' '; }
# Overridable only so the test suite can run this beside other tests' rippers
RIPPER_RE="${DRIVETEST_RIPPER_RE:-^(/usr/local/bin/|[^ ]*/)?cyanrip( |\$)}"
PROBE_RE="${DRIVETEST_PROBE_RE:-^(/usr/local/bin/)?cyanrip .*-I( |\$)}"
ripper_pids() { pgrep -f "$RIPPER_RE" 2>/dev/null; }

wait_drive_free() {   # SECONDS
    local end=$(( $(date +%s) + ${1:-60} ))
    if ! command -v fuser >/dev/null 2>&1; then
        say "drive: UNPROBED whether anything holds $DEV (no fuser here)"
        return 0
    fi
    while drive_held; do
        [ "$(date +%s)" -ge "$end" ] && return 1
        sleep 2
    done
}

disc_ready() { distrobox enter "$BOX" -- sg_turs "$DEV" >/dev/null 2>&1; }

wait_disc_ready() {   # SECONDS
    local end=$(( $(date +%s) + ${1:-60} ))
    until disc_ready; do
        [ "$(date +%s)" -ge "$end" ] && return 1
        sleep "$POLL_SECS"
    done
}

ready_for() {   # WHAT: Platterpus closed, the drive free, a disc ready
    if app_running; then
        say "$1: Platterpus is open; close it and run the same command again"
        return 1
    fi
    if ! wait_drive_free 60; then
        if [ -n "$(ripper_pids)" ]; then
            say "$1: a cyanrip holds $DEV with Platterpus closed ($(holders)); stopping it"
            pkill -KILL -f "$RIPPER_RE"
            wait_drive_free 30 || { say "$1: $DEV is still held: $(holders)"; return 1; }
        else
            say "$1: something other than cyanrip holds $DEV: $(holders)"
            return 1
        fi
    fi
    wait_disc_ready 60 || { say "$1: the drive has not reported a disc ready for a minute"; return 1; }
    say "$1: Platterpus closed, $DEV free, disc ready"
}

# ---- one folder: earlier test files are moved in, never deleted ----------------------

gather() {
    local moved=0 f size want dest
    mkdir -p "$ROOT/earlier"
    # The first sitting of 5 November kept its files in ~/drivemode
    if [ -d "$HOME/drivemode" ]; then
        dest="$(fresh "$ROOT/earlier/drivemode")"
        mv "$HOME/drivemode" "$dest" && moved=$((moved + 1))
        say "moved ~/drivemode (the first sitting's files) to ${dest#"$HOME"/}"
        for f in pioneer-f4 before cyanrip-vendor; do
            for g in "$dest"/dumps/"$f".*; do
                [ -e "$g" ] && [ ! -e "$READS/$(basename "$g")" ] && cp -p "$g" "$READS/"
            done
        done
    fi
    # The sheet downloaded the rig scripts to ~
    for f in drivemode:8598 drivespeed:9492; do
        want="${f#*:}"; f="${f%%:*}"
        [ -f "$HOME/$f.txt" ] || continue
        size="$(wc -c < "$HOME/$f.txt")"
        if [ "$size" = "$want" ] && [ ! -e "$SCRIPTS/$f.txt" ]; then
            mv "$HOME/$f.txt" "$SCRIPTS/$f.txt"
        else
            mv "$HOME/$f.txt" "$(fresh "$ROOT/earlier/$f" .txt)"
        fi
        moved=$((moved + 1))
        say "moved ~/$f.txt into the folder"
    done
    # This script: keep one copy, in ~/platterpus-rig
    case "$(readlink -f "$0")" in
        "$RIG/drivetest.sh") ;;
        *) cp -p "$0" "$RIG/drivetest.sh" 2>/dev/null && say "copied this script to ~/platterpus-rig/drivetest.sh; run it from there from now on" ;;
    esac
    {
        echo "What you may delete by hand once the uploads have reached both sessions."
        echo "Nothing here is deleted by the script. Audio stays only on this machine."
        echo
        case "$(readlink -f "$0")" in
            "$RIG/drivetest.sh") ;;
            *) echo "  rm $(readlink -f "$0")      # the copy you ran first; ~/platterpus-rig/drivetest.sh is the one" ;;
        esac
        echo "  rm -r ~/platterpus-rig/drivetest-r38/earlier   # after its files are in an upload"
        echo "  ls -t ~/.local/share/platterpus/bundles/        # the app's bundles; each upload carries the new ones"
        echo "  ls ~/.local/share/platterpus/uiscript/          # the app's own script-run folders"
    } > "$ROOT/CLEANUP.txt"
    [ "$moved" -gt 0 ] || true
}

# ---- every stage ends here, a stop included -------------------------------------------

kernel_messages() {
    local f
    mkdir -p "$ROOT/kernel"
    f="$(fresh "$ROOT/kernel/stage$STAGE" .txt)"
    {
        echo "# kernel messages since this stage began, about the drive and its bus"
        if journalctl -k --no-pager -o short-iso --since "@$STAGE_START_EPOCH" > "$f.all" 2>&1; then
            grep -iE 'sr[0-9]|cdrom|scsi|sense|ata[0-9]|i/o error|reset|timeout' "$f.all" \
                || echo "(none matched, of $(wc -l < "$f.all") kernel lines)"
        else
            echo "UNPROBED: journalctl -k gave: $(head -c 300 "$f.all")"
        fi
        rm -f "$f.all"
    } > "$f"
}

make_send() {   # LABEL SINCE-FILE: one upload file, and a MANIFEST of what it holds
    local out list=() f rel
    mkdir -p "$ROOT/SEND"
    out="$(fresh "$ROOT/SEND/drivetest-r38-$1-$(date -u +%Y%m%dT%H%M%SZ)" .tar.gz)"
    for f in "$ROOT"/*; do
        case "$(basename "$f")" in SEND|earlier|runs) continue ;; esac
        list+=("${f#"$HOME"/}")
    done
    for f in "$RUNS"/*-logs.tar.gz "$ROOT"/earlier; do
        [ -e "$f" ] && list+=("${f#"$HOME"/}")
    done
    if [ -d "$BUNDLES" ] && [ -e "$2" ]; then
        while IFS= read -r f; do
            list+=("${f#"$HOME"/}")
        done < <(find "$BUNDLES" -maxdepth 1 -type f -name '*.tar.gz' -newer "$2" | sort)
    fi
    ( cd "$HOME" && for rel in "${list[@]}"; do
          if [ -d "$rel" ]; then find "$rel" -type f ! -name '*.flac' ! -name '*.wav'; else echo "$rel"; fi
      done | sort | xargs -d '\n' sha256sum ) > "$ROOT/MANIFEST.txt" 2>/dev/null
    list+=("${ROOT#"$HOME"/}/MANIFEST.txt")
    if tar czf "$out" -C "$HOME" --exclude='*.flac' --exclude='*.wav' "${list[@]}"; then
        say "UPLOAD THIS ONE FILE to both sessions: ~/${out#"$HOME"/} ($(du -h "$out" | cut -f1))"
    else
        say "could not pack $out; send the folder ~/${ROOT#"$HOME"/} itself, without audio"
    fi
}

finish() {   # LABEL SINCE-FILE
    kernel_messages
    make_send "$1" "$2"
    if [ "$NFAIL" -gt 0 ]; then
        # shellcheck disable=SC2088  # a path shown to a person, not expanded
        printf '\n========== %s FAILURE(S) THIS STAGE; the full text is in %s ==========\n' "$NFAIL" "~/${FAIL#"$HOME"/}"
        tail -n 120 "$FAIL"
        printf '========== end of failures ==========\n'
    else
        say "no failures this stage"
    fi
}

stop() {   # WHY [FILE]: write it down, still pack everything, end
    failed "STOPPED" "$1" "${2:-}"
    finish "stage$STAGE-stopped" "$(first_f4)"
    exit 1
}

# ---- before anything ------------------------------------------------------------------

preflight() {
    gather
    app_running && stop "Platterpus is open: close it, then run the same command again"
    # shellcheck disable=SC2012  # the newest by time; these names hold no newline
    [ -x "$APP" ] || APP="$(ls -t "$HOME"/Applications/*latterpus*.AppImage "$HOME"/Downloads/*latterpus*.AppImage 2>/dev/null | head -1)"
    if [ -z "$APP" ] || [ ! -x "$APP" ]; then
        stop "no Platterpus AppImage in ~/Applications or ~/Downloads"
    fi
    [ -x "$CYANRIP" ] || stop "no ripper at ~/.local/bin/cyanrip: repeat phase 0"
    command -v distrobox >/dev/null 2>&1 || stop "no distrobox on this system"
    if ! distrobox enter "$BOX" -- sh -c 'command -v sg_raw && command -v sg_turs && command -v cdrdao && command -v strace' >/dev/null 2>&1; then
        say "tools: installing sg3_utils, cdrdao and strace in the $BOX container (read-only tools; it may ask for your password)"
        distrobox enter "$BOX" -- sudo dnf install -y sg3_utils cdrdao strace > "$ROOT/tool-install.txt" 2>&1 \
            || stop "the tool install did not finish" "$ROOT/tool-install.txt"
    fi
    local f size want
    for f in drivemode:8598 drivespeed:9492; do
        want="${f#*:}"; f="${f%%:*}"
        size="$(wc -c < "$SCRIPTS/$f.txt" 2>/dev/null || echo 0)"
        if [ "$size" != "$want" ]; then
            curl -fsSL -o "$SCRIPTS/$f.txt" "$RIG_BASE/$f.txt" || stop "could not download $f.txt"
            size="$(wc -c < "$SCRIPTS/$f.txt")"
        fi
        [ "$size" = "$want" ] || stop "$f.txt is $size bytes and the sheet says $want: Platterpus has changed it since the sheet was printed; ask both sessions first"
    done
    {
        echo "script sha256 $(sha256sum "$0" | cut -d' ' -f1)"
        echo "app $(basename "$APP") sha256 $(sha256sum "$APP" | cut -d' ' -f1)"
        echo "drivemode.txt sha256 $(sha256sum "$SCRIPTS/drivemode.txt" | cut -d' ' -f1)"
        echo "drivespeed.txt sha256 $(sha256sum "$SCRIPTS/drivespeed.txt" | cut -d' ' -f1)"
        echo "kernel $(uname -r)"
        echo "distrobox $(distrobox version 2>/dev/null | tail -1)"
        echo "rips folder ~/$(rips_dir | sed "s#^$HOME/##")"
    } > "$ROOT/environment.txt" 2>&1
    say "start: stage $STAGE, $(basename "$0") sha256 $(sha256sum "$0" | cut -c1-16), folder ~/${ROOT#"$HOME"/}; sleep ${DRIVETEST_AWAKE:-NOT blocked (no systemd-inhibit lock): keep the machine awake yourself}"
}

dump() {   # NAME COMMANDS: the sheet's dump(), into a name not used yet
    local file
    file="$(fresh "$READS/$1" .txt)"
    distrobox enter "$BOX" -- sh -c "date -u; $2" > "$file" 2>&1
    LAST_DUMP="$file"
    if grep -qiE 'illegal request|not ready|permission denied|command not found' "$file"; then
        failed "read $1" "the drive or the tool reported an error" "$file"
    else
        say "read: $(basename "$file") ($(wc -l < "$file") lines)"
    fi
}

# ---- the two-read check ------------------------------------------------------------------

rc_word() { case "$1" in 0) echo "finished";; 124|137) echo "HUNG, killed at ${CHECK_SECS}s";; *) echo "failed";; esac; }

sample_waits() {   # FLAG FILE: what each cyanrip waits on, every 5 s, until FLAG exists
    local p
    while [ ! -e "$1" ]; do
        for p in $(ripper_pids); do
            printf '%s pid %s state %s wchan %s cmd %s\n' "$(date -u +%H:%M:%S)" "$p" \
                "$(awk '/^State/{print $2}' "/proc/$p/status" 2>/dev/null)" \
                "$(cat "/proc/$p/wchan" 2>/dev/null)" \
                "$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null | cut -c1-80)"
        done >> "$2"
        sleep "$POLL_SECS"
    done
}

pair() {   # FOLDER plain|strace: A, then B 2.4 s later
    local c="$1" how="$2" pa pw tb ra sa rb sb
    run_one() {
        if [ "$how" = strace ]; then
            timeout -k 5 "$CHECK_SECS" distrobox enter "$BOX" -- strace -f -tt -v -s 32 \
                -e trace=openat,ioctl,read,close -o "$1.strace" /usr/local/bin/cyanrip -I -N -d "$DEV" > "$1" 2>&1
        else
            timeout -k 5 "$CHECK_SECS" "$CYANRIP" -I -N -d "$DEV" > "$1" 2>&1
        fi
    }
    rm -f "$c/.pairdone"
    ( s=$(date +%s); run_one "$c/pairA.txt"; echo "$? $(( $(date +%s) - s ))" > "$c/pairA.rc" ) &
    pa=$!
    sample_waits "$c/.pairdone" "$c/waits.txt" &
    pw=$!
    sleep 2.4
    tb=$(date +%s)
    run_one "$c/pairB.txt"; rb=$?
    sb=$(( $(date +%s) - tb ))
    wait "$pa"
    touch "$c/.pairdone"; wait "$pw"; rm -f "$c/.pairdone"
    read -r ra sa < "$c/pairA.rc"
    PAIR_A=$ra; PAIR_B=$rb
    say "check ($how): two reads 2.4 s apart: A exit $ra ($(rc_word "$ra")) after ${sa}s, $(wc -c < "$c/pairA.txt") bytes; B exit $rb ($(rc_word "$rb")) after ${sb}s, $(wc -c < "$c/pairB.txt") bytes"
    sleep 2
    if drive_held; then
        say "check ($how): after the reads ended, a read still held $DEV: $(holders)"
        pkill -KILL -f "$RIPPER_RE" && say "check ($how): stopped the leftover cyanrip read(s)"
        pkill -KILL -x strace 2>/dev/null
    else
        say "check ($how): nothing held $DEV after the reads ended"
    fi
    wait_drive_free 60 || stop "$DEV is still held after the check: $(holders)"
}

do_check() {
    local c t0 ra sa ver toc hung=0 f
    ready_for "check" || return 1
    c="$(fresh "$ROOT/check")"
    mkdir -p "$c"
    t0=$(date +%s)
    timeout -k 5 "$CHECK_SECS" "$CYANRIP" -I -N -d "$DEV" > "$c/solo.txt" 2>&1; ra=$?
    sa=$(( $(date +%s) - t0 ))
    say "check: one read alone: exit $ra ($(rc_word "$ra")) after ${sa}s, $(wc -c < "$c/solo.txt") bytes"
    [ "$ra" = 0 ] || failed "check, one read alone" "exit $ra ($(rc_word "$ra"))" "$c/solo.txt"
    ver="$(grep -ao 'cyanrip [^ ]*+platterpus\.[0-9]*' "$c/solo.txt" | head -1)"
    toc="$(grep -ao 'toc=[0-9+]*' "$c/solo.txt" | head -1)"
    say "check: the ripper says ${ver:-nothing about its version}; the disc's TOC ${toc:-was not printed}"
    [ "$ver" = "$WANT_RIPPER" ] || failed "check" "the ripper is '${ver:-unknown}', and the test is for $WANT_RIPPER" "$c/solo.txt"
    [ -z "$toc" ] || [ "$toc" = "toc=$WANT_TOC" ] || failed "check" "the disc in the drive is not the reference disc (its TOC differs)" "$c/solo.txt"
    wait_drive_free 60 || stop "$DEV is held after the single read: $(holders)"
    pair "$c" plain
    case "$PAIR_A" in 124|137) hung=$((hung + 1));; esac
    case "$PAIR_B" in 124|137) hung=$((hung + 1));; esac
    if [ "$PAIR_A" = 0 ] && [ "$PAIR_B" = 0 ]; then
        say "check: RESULT: two reads at once both finished (one trial)"
    elif [ "$hung" -gt 0 ]; then
        say "check: RESULT: with two reads at once, $hung of 2 stalled with Platterpus closed (one trial); repeating under strace to see where"
        mkdir -p "$c/strace"
        pair "$c/strace" strace
        for f in "$c"/strace/pair?.txt.strace; do
            [ -f "$f" ] && say "check (strace): $(basename "$f"): last call: $(grep -v 'resumed\|exited\|killed' "$f" | tail -1 | cut -c1-200)"
        done
    else
        failed "check, two reads" "A exit $PAIR_A, B exit $PAIR_B, without a stall" "$c/pairB.txt"
    fi
}

# ---- the C2 probe ---------------------------------------------------------------------------

# READ CD (BEh), 26 frames from LBA $2, byte 9 = $3 (12h: audio and C2 error
# pointers, 2646 bytes a frame; 14h: and the block error bits, 2648). Places
# on the reference disc: track 3 starts at LBA 28067 and track 5 at 72570 (the
# TOC minus 150); the wrong samples are 04:04:68, 04:05:17 and 04:11:32 into
# track 3 and 02:24:59 into track 5 (EAC's and CTDB's localisation).
c2_read() {   # FILE LBA BYTE9 BYTES-A-FRAME
    # shellcheck disable=SC2046  # the LBA's four bytes are four arguments
    distrobox enter "$BOX" -- sg_raw -R -o "$1" -r $((26 * $4)) "$DEV" be 00 \
        $(printf '%02x %02x %02x %02x' $(( ($2 >> 24) & 255 )) $(( ($2 >> 16) & 255 )) $(( ($2 >> 8) & 255 )) $(( $2 & 255 ))) \
        00 00 1a "$3" 00 00
}

# shellcheck disable=SC2016  # expanded by the container's shell
c2_flush() { distrobox enter "$BOX" -- sh -c 'for l in 0 26 52 78 104 130 156 182 208 234 260 286; do sg_raw -R -r 61152 /dev/sr0 be 00 $(printf "%02x %02x %02x %02x" 0 0 $((l>>8)) $((l&255))) 00 00 1a 10 00 00 >/dev/null 2>&1; done'; }

do_c2() {
    local c n t lba out solo
    ready_for "C2 probe" || return 1
    solo="$(find "$ROOT" -maxdepth 2 -path "$ROOT/check*/solo.txt" | sort | tail -1)"
    if [ -s "$solo" ] && ! grep -aq "toc=$WANT_TOC" "$solo"; then
        say "C2 probe: skipped, the disc in the drive is not the reference disc"
        return 0
    fi
    c="$(fresh "$ROOT/c2-stage$STAGE")"
    mkdir -p "$c"
    say "C2 probe: start, in ~/${c#"$HOME"/}"
    for t in control:5000 t3a:46422 t3b:46446 t3c:46911 t5:83416; do
        lba="${t#*:}"; t="${t%%:*}"
        for n in 1 2 3; do
            c2_flush
            out="$c/$t-c2-$n.bin"
            if ! c2_read "$out" "$lba" 12 2646 > "$out.txt" 2>&1; then
                failed "C2 probe, $t read $n" "READ CD asking for C2 pointers (byte 9 = 12h) was refused" "$out.txt"
                if [ "$t" = control ]; then
                    say "C2 probe: the drive refused C2 pointers at the control, so the rest is skipped"
                    return 0
                fi
            fi
        done
    done
    c2_flush
    c2_read "$c/t5-c2b-1.bin" 83416 14 2648 > "$c/t5-c2b-1.bin.txt" 2>&1 \
        || failed "C2 probe, t5 with block bits" "READ CD with byte 9 = 14h was refused" "$c/t5-c2b-1.bin.txt"
    if command -v python3 >/dev/null 2>&1; then
        python3 -I - "$c" > "$c/summary.txt" 2>&1 <<'PY'
import pathlib, sys
d = pathlib.Path(sys.argv[1])
for f in sorted(d.glob("*-c2-*.bin")):
    data = f.read_bytes()
    if len(data) != 26 * 2646:
        print(f"{f.name}: {len(data)} bytes, not 26 frames of 2646")
        continue
    flagged = []
    for i in range(26):
        bits = sum(bin(b).count("1") for b in data[i * 2646 + 2352:(i + 1) * 2646])
        if bits:
            flagged.append(f"frame {i} ({bits} bit{'s' if bits != 1 else ''})")
    print(f"{f.name}: " + (", ".join(flagged) if flagged else "no C2 bit set in 26 frames"))
PY
        while IFS= read -r line; do say "C2 probe: $line"; done < "$c/summary.txt"
    else
        say "C2 probe: UNPROBED which frames carry C2 bits (no python3 here); the reads are kept"
    fi
}

# ---- runs -------------------------------------------------------------------------------------

pack() {   # NAME PREFIX: move rip folders aside, pack their logs, never audio
    local rips dest
    PACKED=0
    rips="$(rips_dir)"
    compgen -G "$rips/$2*" >/dev/null || { say "$1: no $2* rip folders in ~/${rips#"$HOME"/}"; return 0; }
    dest="$(fresh "$RUNS/$1")"
    mkdir -p "$dest"
    mv "$rips"/"$2"* "$dest"/
    PACKED="$(find "$dest" -mindepth 1 -maxdepth 1 -type d | wc -l)"
    tar czf "$dest-logs.tar.gz" --exclude='*.flac' --exclude='*.wav' -C "$RUNS" "$(basename "$dest")"
    say "$1: moved $PACKED rip folder(s) to ~/${dest#"$HOME"/}; packed its logs ($(du -h "$dest-logs.tar.gz" | cut -f1))"
}

# Two `cyanrip -I` disc reads at once while the app runs means it abandoned the
# older ("superseded by a newer disc probe"), so the older is stopped.
probe_guard() {   # APP-PID LOG
    local pids newest p
    while kill -0 "$1" 2>/dev/null; do
        pids="$(pgrep -f "$PROBE_RE" 2>/dev/null | paste -sd, -)"
        if [ -n "$pids" ] && [ "$(echo "$pids" | tr ',' '\n' | wc -l)" -gt 1 ]; then
            newest="$(ps -o pid= --sort=start_time -p "$pids" 2>/dev/null | tail -1 | tr -d ' ')"
            for p in ${pids//,/ }; do
                [ "$p" = "$newest" ] && continue
                kill -KILL "$p" 2>/dev/null && printf '%s | probe guard: stopped the abandoned disc read, pid %s; pid %s keeps the drive\n' "$(stamp)" "$p" "$newest" >> "$2"
            done
        fi
        sleep 0.5
    done
}

APP_RUNS_EMPTY=0

run_app() {   # LETTER RIG-SCRIPT PREFIX
    local attempt out rc ended ver app guard_log
    if [ "$APP_RUNS_EMPTY" -ge 2 ]; then
        failed "Run $1" "not started: the last two app runs ripped nothing, so this one would not either"
        return 0
    fi
    pack "before-$1" "$3"
    for attempt in 1 2; do
        ready_for "Run $1" || stop "Run $1 could not start"
        out="$(fresh "$OUT/run$1" .txt)"
        guard_log="$out.guard"
        say "Run $1: start (attempt $attempt), $(basename "$2"); the app's output also goes to ~/${out#"$HOME"/}"
        "$APP" --run-script "$2" > >(tee "$out") 2>&1 &
        app=$!
        probe_guard "$app" "$guard_log" &
        wait "$app"; rc=$?
        sleep 1
        if [ -s "$guard_log" ]; then tee -a "$TL" < "$guard_log"; fi
        ver="$(grep -aoE 'platterpus [0-9][0-9.]* \(build [0-9a-f]+\)' "$out" | head -1)"
        ended="$(grep -a 'ui script run ended:' "$out" | tail -1 | sed -E 's/^.*ui script run ended: //')"
        say "Run $1: end, app exit $rc, ${ver:-app version not in its output}; ${ended:-no 'run ended' line in its output}"
        case "$ver" in "$WANT_APP "*) ;; *) failed "Run $1" "the app is '${ver:-unknown}', and the test is for $WANT_APP" "$out" ;; esac
        grep -aq 'superseded by a newer disc probe' "$out" && say "Run $1: the app started a second disc read while the first ran"
        pack "run$1" "$3"
        if [ "$PACKED" -gt 0 ]; then
            APP_RUNS_EMPTY=0
            case "$ended" in *fail*) failed "Run $1" "it made $PACKED rip(s) and reported: $ended" "$out" ;; esac
            return 0
        fi
        failed "Run $1, attempt $attempt" "the run ended without a rip: ${ended:-no 'run ended' line}" "$out"
        [ "$attempt" = 1 ] && say "Run $1: nothing was ripped, so the whole run starts again once"
    done
    APP_RUNS_EMPTY=$((APP_RUNS_EMPTY + 1))
}

phase2() {   # the sheet's phase 2, word for word, in a folder of its own
    local t9 nbin
    ready_for "phase 2" || { failed "phase 2" "not started"; return 0; }
    t9="$(fresh "$ROOT/track9")"
    mkdir -p "$t9"
    say "phase 2: start, in ~/${t9#"$HOME"/}"
    (
        cd "$t9" && date -u > times.txt
        # shellcheck disable=SC2016  # the sheet's command, expanded by the container's shell
        flush() { distrobox enter ripping -- sh -c 'for l in 0 26 52 78 104 130 156 182 208 234 260 286; do sg_raw -R -r 61152 /dev/sr0 be 00 $(printf "%02x %02x %02x %02x" 0 0 $((l>>8)) $((l&255))) 00 00 1a 10 00 00 >/dev/null 2>&1; done'; }
        for n in 1 2 3; do
            flush; { echo "raw$n"; distrobox enter ripping -- bash -c "time sg_raw -R -o raw$n.bin -r 39168 /dev/sr0 be 00 00 02 38 98 00 00 10 10 01 00"; } >> times.txt 2>&1
            flush; { echo "q$n"; distrobox enter ripping -- bash -c "time sg_raw -R -o q$n.bin -r 37888 /dev/sr0 be 00 00 02 38 98 00 00 10 10 02 00"; } >> times.txt 2>&1
        done
        ls -l ./*.bin >> times.txt
        distrobox enter ripping -- cdrdao read-toc --device /dev/sr0 "$t9/cdrdao.toc" > cdrdao-output.txt 2>&1
    )
    nbin="$(find "$t9" -name '*.bin' -size +0 | wc -l)"
    say "phase 2: end, $nbin of 6 track 9 reads saved"
    [ "$nbin" = 6 ] || failed "phase 2" "$nbin of 6 track 9 reads saved" "$t9/times.txt"
    [ -s "$t9/cdrdao.toc" ] || failed "phase 2" "cdrdao wrote no TOC" "$t9/cdrdao-output.txt"
}

wipe_break() {   # open the tray; wait for the disc to go out and come back
    local end gone=0
    say "WIPE THE DISC NOW: the tray is opening. Wipe it from the centre outward with a soft dry cloth, put it back and close the tray; the test carries on by itself. Say what cloth with: bash ~/platterpus-rig/drivetest.sh note \"...\""
    distrobox enter "$BOX" -- eject "$DEV" >/dev/null 2>&1 || eject "$DEV" >/dev/null 2>&1 \
        || say "the tray did not open by itself: press the drive's button"
    end=$(( $(date +%s) + WAIT_DISC_SECS ))
    while [ "$(date +%s)" -lt "$end" ]; do
        if disc_ready; then [ "$gone" = 1 ] && break; else gone=1; fi
        sleep "$POLL_SECS"
    done
    disc_ready || stop "the disc did not come back within $((WAIT_DISC_SECS / 60)) minutes; put it in and run: bash ~/platterpus-rig/drivetest.sh 1"
    [ "$gone" = 1 ] || failed "wipe" "the drive never reported the disc out"
    say "disc back; $SETTLE_SECS seconds for it to settle"
    sleep "$SETTLE_SECS"
}

# ---- steps done once; "redo NAME" repeats one ------------------------------------------------------

DONE="$ROOT/.done"
once() {   # NAME COMMAND...
    local key="$1"; shift
    if [ -f "$DONE" ] && grep -qx -- "$key" "$DONE"; then
        say "$key: already done, skipped (redo $key repeats it)"
        return 0
    fi
    "$@" && echo "$key" >> "$DONE"
}

first_f4() { ls "$READS"/pioneer-f4.txt 2>/dev/null || echo "$TL"; }

step_first_reads() {
    [ -s "$READS/pioneer-f4.txt" ] || dump pioneer-f4 "sg_raw -R -r 256 /dev/sr0 $F4_CDB"
    [ -s "$READS/before.txt" ] || dump before "$STD_QUERIES"
    return 0
}

step_perfect_reads() {
    touch "$ROOT/.phase3-start"
    dump pioneer-f4-perfect "sg_raw -R -r 256 /dev/sr0 $F4_CDB"
    dump after-perfect "$STD_QUERIES"
}

f4_rows() { grep -E '^ +[0-9a-f]+ +[0-9a-f]{2} ' "$1" | cut -c1-58; }

step_restored() {
    local first now
    dump pioneer-f4-restored "sg_raw -R -r 256 /dev/sr0 $F4_CDB"
    first="$(f4_rows "$READS/pioneer-f4.txt" 2>/dev/null)"
    now="$(f4_rows "$LAST_DUMP")"
    if [ -z "$first" ]; then
        say "restored: UNPROBED, no settings bytes in the first read (pioneer-f4.txt)"
    elif [ -z "$now" ]; then
        failed "restored" "the drive gave no settings bytes this time" "$LAST_DUMP"
    elif [ "$first" = "$now" ]; then
        say "restored: the drive's 256 settings bytes match the first read (pioneer-f4.txt)"
    else
        failed "restored" "the drive's settings bytes DIFFER from the first read; compare pioneer-f4.txt with $(basename "$LAST_DUMP")" "$LAST_DUMP"
    fi
}

# ---- stages -------------------------------------------------------------------------------------------

case "$STAGE" in
1)
    preflight
    once first-reads step_first_reads
    once check do_check
    once c2 do_c2
    once runA run_app A "$SCRIPTS/drivemode.txt" dm
    once wipe wipe_break
    once runB run_app B "$SCRIPTS/drivemode.txt" dm
    once runC run_app C "$SCRIPTS/drivespeed.txt" ds
    once phase2 phase2
    finish stage1 "$(first_f4)"
    say "Stage 1 done. Next: phase 3 in Windows (the sheet's 3.1 and 3.2), then: bash ~/platterpus-rig/drivetest.sh 3"
    ;;
3)
    preflight
    once perfect-reads step_perfect_reads
    once c2-perfect do_c2
    once runD run_app D "$SCRIPTS/drivemode.txt" dm
    finish stage3 "$ROOT/.phase3-start"
    say "Stage 3 done. Next: Windows, set Pure Read back (the sheet's 3.4a), then in Bazzite: bash ~/platterpus-rig/drivetest.sh 4"
    ;;
4)
    gather
    once restored step_restored
    if [ -e "$ROOT/.phase3-start" ]; then since="$ROOT/.phase3-start"; else since="$(first_f4)"; fi
    finish stage4 "$since"
    say "Stage 4 done. Phase 4 is the app's menu: Tools, Advanced, Run acceptance test, Full."
    ;;
note)
    shift
    [ $# -gt 0 ] || { echo "write the note after the word note"; exit 2; }
    say "note: $*"
    ;;
redo)
    [ -n "${2:-}" ] || { echo "say which step: first-reads, check, c2, runA, wipe, runB, runC, phase2, perfect-reads, c2-perfect, runD, restored"; exit 2; }
    if [ -f "$DONE" ]; then grep -vx -- "$2" "$DONE" > "$DONE.tmp"; mv "$DONE.tmp" "$DONE"; fi
    say "redo: $2 will run again next time its stage runs"
    ;;
send)
    finish "${2:-now}" "$(first_f4)"
    ;;
*)
    sed -n '2,33p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
