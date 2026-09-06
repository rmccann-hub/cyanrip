# Rig session 2026-09-05 — build `978f9b0`, Platterpus **0.6.37** (not 0.6.38)

**Date the session by its build.** Ours is `978f9b0` =
`cyanrip 0.9.4-rc2+platterpus.11`, the round-15 pin, on a 14-track disc,
`Total time: 59:42.57`.

Delivered as `platterpusbundle20260905t180633z.tar.gz`,
`sha256 9520d635…c8e0ca10`. Filed by `tools/ingest-bundle.py`, which reads the
run's verdict **before** anything else and derives the not-filed list as a set
difference: **34 filed, 255 named-not-filed**, all 289 checksummed in
`SHA256SUMS`. The omissions are derived, not recalled — that is the tool's whole
reason to exist, and it exists because the 2026-09-03 filing note was written
from memory and made two unread verdict files invisible.

## The run passed, and the app half is not the one the lap declared

    report.json    ok = True    {pass: 227, fail: 0, error: 0, skipped: 0, blocked: 0, info: 1}
    transcript.txt no [ FAIL ] lines

**Their lap 13 declares the run is on `0.6.38`.** The bundle says otherwise, in
three independent places, and one of them is the run declaring it of itself:

    extra…/transcript.txt:360   INFO  platterpus/version  0.6.37 (build f3b60a0)
    extra…/report.json          app_version = '0.6.37'
    all 8 cyanrip logs          Consumer:  platterpus/0.6.37

`f3b60a0` is the **previous** pin, from their lap 12. The string `0.6.38` appears
**0 times** in 289 entries.

**And the script is the older one too**, which matters more than the version
string because it is behavioural. Their §C1 says `0.6.38` introduces
`expect-log-well-formed`, `expect-secure-rerip` and `expect-identified`. This
transcript contains **none** of the three; it contains `expect-tracks 2+` (×10)
and `expect-status cancelled` (×3) — the checks their own §A1 tabulates as
**satisfiable by finding nothing**. The `fullacceptance.txt` shipped in the same
envelope as lap 13 *does* carry all three new verbs, so the fixed script exists;
this run was not produced by it.

**What that does and does not mean.** Their §A1: *"None of these would have
FAILED the run. All four would have PASSED it, which is worse: a green transcript
over three untested archival claims and 22 unfailable evidence rows."* This run is
green. By their own analysis a green from this script does not establish those
archival claims. **Whether CC-1 is met is therefore theirs to assess, not ours** —
S-14, a failure in their half is not a `HOLD` on ours. **Why** the older build ran
is `unknown (not determinable from the bundle)`.

**Our `Consumer:` line is correct.** It records what the caller claimed, verbatim
and explicitly unverified — that is the contract. The claim is theirs.

## Our half: no defect, on every criterion their §J names

Their lap 13 §J pre-commits to `GO` unless the run finds, in the pin: a non-zero
`Ripping errors`, a missing or malformed completion footer, an unclassifiable
build tag, a parsed log line changed without notice, a rejected argv, or a hang
attributable to the ripper. Measured here, across all 8 rips:

| | |
|---|---|
| first line of every cyanrip log | `cyanrip 0.9.4-rc2+platterpus.11 (platterpus-fork-g978f9b0)`, 8 of 8 |
| `Ripping errors:` | `0`, 8 of 8 |
| `Rip completed:` | `yes` — two whole-disc (14 of 14), five 2-track, one 3-track |
| `cyanrip -Y` on each log | **exit 0, 8 of 8**, run by a *later* build than wrote them |
| unclassifiable build tag | none |

**Not a `HOLD`, and our `GO` stands** — now positively supported rather than
merely unrefuted.

## What this session establishes about the pin

| | |
|---|---|
| pregap source | **33 × `sub-channel (not signalled by TOC)`**, 8 × `lead-in` |
| secure re-read | 12 converged after 3 reads, **2 did NOT converge (repeat limit hit)**, 27 not attempted |
| AccurateRip | `found` on all 8 — **the network path RAN** |
| read stalls | populated and plural: `15 reads exceeded 10s; longest 20s (track 1, LSN 11916)`, and two more |

**The AccurateRip line is worth stating plainly.** `docs/AUDIT-2026-09-05.md` §1.3
records three live defects in that response parser — an unchecked `av_realloc`
feeding a `memcpy`, a `strcmp` on a `content_type` that is NULL when no header is
sent, and a `strstr` over a never-NUL-terminated buffer — on a path **no scenario
in our suite can reach**, because all 40 hardcode `-N -A -U`. This run reached it
eight times and did not trip it, which is what a well-behaved server produces.
**That is not evidence the defects are unreachable.** It is one sample of one
network, and the reachable case is a 200 with a non-`octet-stream` body — a
captive portal or proxy interstitial.

## The cancel scenarios, a third time

`cancel me` and `after cancel` again **do not show a rip cancel**. Both carry
`Ripping errors: 0` and `Rip completed: yes`, and the only `cancel` verbs in the
transcript are dialog dismissals — `cancelled 'Set up drive'`,
`cancelled 'Settings'`. Same reading as 2026-08-26 and 2026-09-03: **a folder name
is not evidence.** Read `Invoked as:` before crediting a scenario with what its
name claims.

## Still untouched by any run

C2 (the drive reports it unsupported), `-f`, damaged media, CD-TEXT from a disc
that has some, and `-x` alone on a drive that goes on to rip.
