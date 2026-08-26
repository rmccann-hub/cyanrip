## Unit tests
## ==========
## Built from the objects they test, avtransport-style.
unit_test_deps = [
    dependency('libavutil'),
    dependency('libavcodec'),
    dependency('libcdio'),
    dependency('libcdio_paranoia'),
]

fun512_test = executable('fun512_test',
    sources: [ 'fun512.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'fun512.c' ]),
    dependencies: unit_test_deps,
)
test('FUN512 checksum', fun512_test)

naming_test = executable('naming_test',
    sources: [ 'naming.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'naming.c' ]),
    dependencies: unit_test_deps,
)
test('Naming schemes', naming_test)

## Includes pregap.c rather than linking it: the Q sub-channel helpers are
## static, and this is the one pregap path no disc image can reach.
subq_test = executable('subq_test',
    sources: [ 'subq.c' ],
    include_directories: [ '../src' ],
    dependencies: unit_test_deps + [ dependency('libcdio_paranoia') ],
)
test('Q sub-channel decoding', subq_test)

## Whether a pre-gap earns an INDEX 00. Header-only, no objects: the case it
## exists to get right needs a pre-gap that is signalled AND zero frames long,
## and no image driver produces one -- measured on a purpose-built bincue
## fixture, which came back "unknown (sub-channel unreadable)".
cuegap_test = executable('cuegap_test',
    sources: [ 'cuegap.c' ],
    include_directories: [ '../src' ],
    dependencies: unit_test_deps,
)
test('Cue pre-gap decision', cuegap_test)

## The sample-peak cross-check decision. Header-only, so no objects: the point
## is that the firing path is unreachable from any disc image, and the logic
## therefore has to be exercised on its own.
peak_test = executable('peak_test',
    sources: [ 'peak.c' ],
    include_directories: [ '../src' ],
    dependencies: unit_test_deps,
)
test('Peak cross-check', peak_test)

## Links the watchdog object and supplies its own cyanrip_log(), so the
## assertions are against the formatted message rather than scraped stdout.
## Deliberately calls nothing while a read is outstanding: that is the property
## the callback-driven version lacked.
stall_test = executable('stall_test',
    sources: [ 'stall.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'stall_watchdog.c' ]),
    dependencies: unit_test_deps + [ dependency('threads') ],
)
test('Stall watchdog', stall_test, timeout: 60)

## Pins every wording of the `Cache probe:` line. Eight of the nine are
## reachable only from a real drive, and no real drive ran this code until
## 2026-08-10 -- so until now the only wording anyone could read was whichever
## one their disc happened to produce. That first run exposed two defects; this
## is what stops them coming back.
cacheprobe_test = executable('cacheprobe_test',
    sources: [ 'cacheprobe.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'cache_probe.c', 'stall_watchdog.c' ]),
    dependencies: unit_test_deps + [ dependency('threads') ],
)
test('Cache probe wording', cacheprobe_test)

## Links the diagnostics object to drive it past its own retention cap, which
## no rip can reach: an image rip prints ~124 messages against a 20000 cap, so
## the truncation path shipped head-only -- keeping the first lines and
## dropping the last, which is the one that explains a failure.
diag_test = executable('diag_test',
    sources: [ 'diag.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'diagnostics.c', 'stall_watchdog.c' ]),
    dependencies: unit_test_deps + [ dependency('threads') ],
)
test('Diagnostics retention', diag_test)

## Drives the record writer itself and reads back what it wrote.
##
## A mutation sweep of src/cyanrip_log.c scored 44.3%: of 88 single-operator
## changes, 49 were changes the WHOLE suite agreed were fine. Twenty were in the
## AccurateRip verdict -- the strongest claim the log makes -- because every
## scenario passes -A and the verdict needs a network the suite does not have,
## so the surface was unreachable and therefore unasserted. Same for four of the
## six pregap provenances, which need a drive's Q sub-channel.
##
## cyanrip_log_track_end() reads settings and a track struct and calls neither,
## so the states are simply BUILT: point ctx->logfile[0] at a tmpfile, fill the
## track in, call the shipped object, compare the bytes it wrote against the
## contract wording. Not a mock -- cyanrip_log.c and accurip.c are linked
## unmodified, and libcurl comes with accurip.c rather than being used.
logrender_test = executable('logrender_test',
    sources: [ 'logrender.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'cyanrip_log.c', 'accurip.c' ]),
    dependencies: unit_test_deps + [ dependency('threads'), dependency('libcurl') ],
)
test('Log rendering', logrender_test)

## Integration tests
## =================
## Rip the disc image fixtures with the built binary and verify the
## finished files.
python = import('python').find_installation()

## Audio checksum mirror
## =====================
## tools/audio-checksums.py reimplements src/checksums.h in Python so a rip's
## files can be checked against a rip's log -- which is how "14/14 bit-perfect
## vs EAC" stopped being somebody's report and became a command. Two
## implementations of one algorithm drift silently; this is what notices.
test('Audio checksum mirror', python,
     args: [ files('../tools/audio-checksums.py'), 'self-test' ])

## Rig tools
## =========
## The two scripts we hand the operator and ask them to run on hardware nobody
## here can reach. Both have reported a reassuring status over a check that had
## not happened: `cdparanoia-cache` said cd-paranoia "declined to answer" on a
## run where it had printed the figure (`^` under re.M does not match after the
## `\r` cd-paranoia separates progress with), and `audio-vs-log` graded an
## undecodable file as an expected re-rip supersede. Neither is visible on a
## green suite, because passing is what those checks do when they find nothing.
##
## `digest` added eight more within an hour of being written -- a silently
## dropped duplicate track number, an abort that put the reason on stderr where
## a pasted block could not carry it, and four argument values accepted that
## describe no disc. New code is not safer than old code.
test('Rig tools', python, args: [ files('rigcheck.py') ])

## Golden reference freshness
## ==========================
## The reference Platterpus checks its parser against carries the version and
## the compiled-in handshake state, so it goes stale on a bump AND on a new lap
## file. The only existing guard read the banner's version and its dirty
## marker, so the shipped copy claimed `Handshake: round 8 lap 1` while the tree
## was at round 9 lap 1 and nothing could see it. This re-runs the canonical rip
## and diffs, normalising only wall-clock fields, the invocation line, the build
## tag and the log's own checksum.
test('Golden reference freshness', python,
     args: [ files('../tools/gen-golden-reference.py'), '--check',
             '--binary', cyanrip_exe.full_path() ],
     depends: cyanrip_exe,
     timeout: 300)

## Interrupted sample freshness
## ===========================
## The golden reference is a rip that COMPLETES, so it carries none of the
## lines a consumer sees when a rip is stopped -- and after round 12 that is a
## shape Platterpus has to parse. docs/sample-interrupted.log is one real
## artifact of it.
##
## Checked by line shape, never byte for byte, and the difference is the point:
## where the signal lands decides how many frames were read and how many track
## blocks exist, so a body diff would fail on every run for a reason that says
## nothing about the format. This asserts the committed file still carries the
## shapes a rip interrupted right now produces, which is what catches a
## reworded line.
test('Interrupted sample freshness', python,
     args: [ files('../tools/gen-golden-reference.py'), '--interrupted',
             '--check', '--binary', cyanrip_exe.full_path() ],
     depends: cyanrip_exe,
     timeout: 300)

## Argument-surface probe (seam-rules S-9/S-11)
## ===========================================
## Black-box: runs the real binary across every numeric and string argument at
## below-min / min / typical / max / one-past, and FAILS if any value a caller
## set vanishes without a refusal. A silently ignored argument is the outcome
## S-9 most wants written down, and this is the check that keeps the shared
## command table honest between rounds rather than at the moment it was written.
test('Argv surface probe', python,
     args: [ files('../tools/probe-argv-surface.py'), '--gate',
             '--binary', cyanrip_exe.full_path() ],
     depends: cyanrip_exe,
     timeout: 300)

## Handshake wire conformance
## ==========================
## A lap can pass every other test in this suite and still be unfit to send.
## Two round-8 laps reached Platterpus missing HANDSHAKE-APP-VERSION,
## HANDSHAKE-RIPPER-VERSION and HANDSHAKE-PIN -- fields PROTOCOL.md C9 requires
## on any round >= 8 file and tells the receiving gate to refuse on -- because
## `meson test` was green and `tools/release-gate.py` was never run. Green said
## nothing about it.
##
## This asserts only well-formedness, never closure: an OPEN round is the normal
## state and must not fail a build.
## Sent laps are immutable
## =======================
## Round 9 lap 3 was sent and then edited twice -- by us, one lap after we
## criticised Platterpus for the same thing, and while telling ourselves the
## lap was "still DRAFT". It was not; it had been handed over. Nothing caught
## it because every check we had was about a file's CONTENT and none about its
## IDENTITY OVER TIME. Adopted from Platterpus's guard, which is better than
## anything we had.
test('Sent laps are immutable', python, args: [ files('sent_laps.py') ])

test('Handshake wire conformance', python,
     args: [ files('handshake_wire.py'), meson.project_source_root() ])

## Release gate
## ============
## The "no release while a round is open" rule used to be prose only. This is
## the check that executes it, and these are the ways it could wrongly say yes.
test('Release gate', python, args: [ files('release_gate.py') ])

## Settled facts, and the seam checker
## ==================================
## BOTH OF THESE WERE BUILT TO CATCH MISTAKES AND THEN RUN BY NOTHING.
##
## `check-settled.py` re-runs every command in docs/SETTLED.md, so a fact
## nobody re-derives cannot go quietly stale. `seam-check.py` grades every lap
## in the record against the shared protocol. Both were written on 2026-08-26
## and neither was wired to anything, so each only ran when somebody remembered
## -- which is the failure mode they exist to remove, reproduced in the act of
## building them. Same shape as HANDSHAKE-SHARED-HASHES: declared for eight
## rounds and read by nothing.
##
## seam-check runs in --gaps mode here rather than over every lap: grading
## inbound laps is triage a human reads, and a peer's legitimately-different
## holdings would fail the suite for something that is not our defect. --gaps
## audits OUR record for absent lap numbers and cannot fail for anything the
## other side did.
## The instrumented sweep
## ======================
## tests/rip_images.py carries three `runtime error` assertions, written while
## chasing the CD-Extra session-gap underflow. The committed build is
## b_sanitize=none -- the binary carries ZERO UBSan symbols -- so UBSan can
## never print that string and those three checks CANNOT FAIL. They have been
## decoration since that investigation ended, and meson setting ASAN_OPTIONS
## for every test regardless of build options is what made it invisible.
##
## Deleting them would be the wrong fix: signed overflow, a shift out of range,
## a bad index and a NULL deref are exactly what turns an archival record into a
## confident wrong number, and this program does lsn arithmetic on every track.
## So the suite runs them against a build where they can fire.
##
## MEASURED before wiring it in: ~7 s to configure and build the instrumented
## tree from nothing, ~16 s for all 37 image scenarios under it. It roughly
## doubles the suite, and it makes a whole class of defect un-omittable.
##
## The tool verifies the binary really is instrumented before believing a clean
## run -- a sanitizer sweep over an uninstrumented build reports zero findings
## and means nothing, the same shape as a mutation sweep whose mutants are all
## killed by a check that hashes the source.
test('Sanitizer sweep', python, args: [ files('../tools/sanitize-run.py') ],
     timeout: 900)

test('Settled facts', python, args: [ files('../tools/check-settled.py') ])
test('Seam record audit', python, args: [ files('../tools/seam-check.py'), '--gaps' ])


rip_scenarios = [
    'info',
    'cli',
    'basic',
    'pregap',
    'mixed',
    'nrg',
    'filters',
    'album_loudness',
    'contract_covers_log',
    'art',
    'cue_only',
    'errors',
    'cdtext',
    'reporting',
    'metadata',
    'duration',
    'handshake',
    'early_log',
    'diagnostics',
    'contract_build',
    'contract_exit_codes',
    'status_is_current',
    'format_guard',
    'cue_isrc',
    'version_matrix',
    'exit_codes',
    'reference',
    'paranoia',
    'verify_log',
    'interrupt',
    'interrupt_deadlock',
    'cache_probe_only',
    'artifacts_are_tracked',
    'sanitize',
    'enhanced_cd',
    'contract_diagnostics',
    'contract_composed',
    'abort_footer',
]

# The scenarios are told which build configuration they are testing, because
# one of them -- `handshake` -- asserts a rendering that DEPENDS on it. The
# released suffix is chosen by -Ddeclare_released at build time, so a test that
# guesses can only be right for one of the two builds, and the one it was wrong
# for is the one we ship: the shipping configuration failed 2 of 41 until this
# existed. Derived from the option rather than sniffed from the binary.
declared_env = 'CYANRIP_DECLARED_RELEASED=' + (get_option('declare_released') ? '1' : '0')

foreach s : rip_scenarios
    test(s, python,
         args: [ files('rip_images.py'), cyanrip_exe,
                 meson.current_source_dir() / 'fixtures', s ],
         env: [ declared_env ],
         suite: 'images',
         timeout: 120)
endforeach
