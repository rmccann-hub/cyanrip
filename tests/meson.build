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

## The read kept at the -Z repeat limit: the rule in spool.h, which a disc
## image reaches only through the shim and AccurateRip not at all.
spool_test = executable('spool_test',
    sources: [ 'spool.c' ],
    include_directories: [ '../src' ],
)
test('Read kept at the repeat limit', spool_test)

## Includes accurip.c rather than linking it: the response helpers are static,
## and this is the one path NO disc image can reach -- rip_images.py passes
## -N -A -U on every scenario, so crip_fill_accurip() returns before any of it.
## Three defects lived there. The over-read cases need the instrumented build
## to detect the read itself: meson test -C build-asan 'AccurateRip response'.
arresp_test = executable('arresp_test',
    sources: [ 'arresp.c' ],
    include_directories: [ '../src' ],
    dependencies: unit_test_deps + [ dependency('libcurl') ],
)
## The recorded response is the reference disc's dBAR file, fetched once on
## 2026-09-27; the rig log is a real drive's rip of that disc, whose matches the
## parse is checked against. So the parser's settled fact no longer needs the
## network to re-check (docs/KNOWN-ISSUES.md, docs/SETTLED.md). The log is a
## byte-for-byte copy of the 2026-09-10 session's, made before HR-2 moved run
## evidence off this branch: a file the build names must be in the checkout,
## and `meson setup` failed outright without it (tests/fixtures/evidence/
## SOURCES.tsv names each copy's source and SHA-256).
test('AccurateRip response', arresp_test,
     args: [ files('fixtures/accurip-dBAR-014-001d420f-013bb370-e20dfe0e.bin'),
             files('fixtures/evidence/rig-2026-09-10-ddc1e8c/rips/secure-reread.log') ])

## What a cover art fetch accepts (review C items 1.5 and 2.3): the Cover Art
## DB over HTTPS only, an image no larger than the cap, and a URL -C gives
## keeping its own scheme on a handle the DB used. coverart.c is included, as
## arresp.c includes accurip.c, since no scenario reaches the network.
coverart_net_test = executable('coverart_net_test',
    sources: [ 'coverart_net.c' ],
    include_directories: [ '../src' ],
    dependencies: unit_test_deps + [ dependency('libavformat'),
                                     dependency('libcurl') ],
)
test('Cover art fetch limits', coverart_net_test)

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

## A SPURIOUS WAKEUP, CONSTRUCTED RATHER THAN WAITED FOR.
##
## pthread_cond_wait() may return without the predicate holding -- POSIX says
## so -- and the FIFO's three waits were guarded by a single `if`. In
## fifo_pop() that fell straight through to `out = ctx->queued[0]` with
## num_queued still 0, reading a slot nothing had written and then decrementing
## the count to -1.
##
## Waiting for a real spurious wakeup gives a test that fails once a year on
## somebody else's machine. But to the WAITER a spurious wakeup is exactly "the
## condition variable was signalled and the predicate did not change", and that
## is producible on demand: signal cond_in with the queue empty. The waiter
## must not be able to tell the difference, which is the property under test.
##
## REVERT-PROVED, and the result is not subtle: with the single `if` restored,
## this test SEGFAULTS -- exit 139, not a failed assertion. That is what the
## defect actually was.
##
## It includes fifo_frame.c rather than linking it, because CRFrameFIFO and its
## condition variables are private to the translation unit that instantiates
## the template. Same move as tests/subq.c with pregap.c, and for the same
## reason: reaching them is what makes the scenario constructible.
fifo_test = executable('fifo_test',
    sources: [ 'fifo.c' ],
    include_directories: [ '../src' ],
    dependencies: unit_test_deps + [ dependency('threads') ],
)
test('FIFO spurious wakeup', fifo_test, timeout: 60)

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

## The `Accurate stream:` line reads page 2Ah of a MODE SENSE reply, which only
## a drive sends. The parse is pure, so it is driven here with built replies:
## the bit set and clear, block descriptors before the page, the page after
## another, a reply cut short, and no page 2Ah at all. The `Recordable:`
## line's every wording, from the drive's current profile, is pinned beside it,
## with that profile read from GET CONFIGURATION's header on a reply that lists
## CD-ROM last, where libcdio's own search gives its 0xffff placeholder.
drivecaps_test = executable('drivecaps_test',
    sources: [ 'drivecaps.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'drive_caps.c' ]),
    dependencies: unit_test_deps,
)
test('Accurate stream and recordable medium from the drive', drivecaps_test)

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

## The cache probe's evidence block, in its OWN binary because crip_diag_write()
## writes one record per process -- a second writer in diag_test got an empty
## file and failed for a reason that looked nothing like the latch.
##
## It stubs crip_cache_evidence() rather than linking cache_probe.c, and that is
## what makes it possible at all: the real probe REFUSES on an image driver, so
## no fixture in this repository can ever make it emit a series. Driving the
## struct reaches a state the harness cannot drive the program into -- the same
## move as splitting the Q sub-channel decode out for tests/subq.c.
diagcache_test = executable('diagcache_test',
    sources: [ 'diagcache.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'diagnostics.c', 'stall_watchdog.c' ]),
    dependencies: unit_test_deps + [ dependency('threads') ],
)
test('Cache probe evidence', diagcache_test)

## The -j record's /8 fields, round 32 (our lap 1 S10, Platterpus's lap 2 S7
## and S8). Their states are mostly out of an image's reach: libcdio's image
## drivers never report the ISRC capability, no image has sub-channel
## pre-emphasis, and -f on an image ends only with no AccurateRip entry. So the
## context is BUILT, as for diagcache_test, and each record is written by a
## forked child because crip_diag_write() writes one record per process.
diagrecord_test = executable('diagrecord_test',
    sources: [ 'diagrecord.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'diagnostics.c', 'stall_watchdog.c' ]),
    dependencies: unit_test_deps + [ dependency('threads') ],
)
test('Diagnostics record fields', diagrecord_test)

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
## contract wording. Not a mock -- cyanrip_log.c, accurip.c and drive_caps.c
## are linked unmodified, and libcurl comes with accurip.c rather than being
## used.
logrender_test = executable('logrender_test',
    sources: [ 'logrender.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'cyanrip_log.c', 'log_escape.c', 'accurip.c', 'drive_caps.c' ]),
    dependencies: unit_test_deps + [ dependency('threads'), dependency('libcurl') ],
)
test('Log rendering', logrender_test)

## The log's formatter: every conversion this program uses against the C
## library's own vsnprintf(), and each escape against the exact text
## src/log_escape.h promises. Item 3.1 of the claude-code-skills session's
## review of 2026-10-26: a value carrying a line break started a line of its
## own, so a CD-TEXT title could print `Accurip: accurately ripped`.
logescape_test = executable('logescape_test',
    sources: [ 'logescape.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'log_escape.c' ]),
    dependencies: unit_test_deps,
)
test('Log value escaping', logescape_test)

## The two shims below are LD_PRELOAD interposers on glibc's names (fopen64,
## __vfprintf_chk) through dlsym(RTLD_NEXT). That is Linux's dynamic loader:
## macOS ignores LD_PRELOAD and hides RTLD_NEXT under the _XOPEN_SOURCE this
## project sets, and Windows has neither, so CI's first macOS and MinGW runs
## failed to build them. They are built on Linux only, and elsewhere the
## scenarios that rip through them say UNPROBED -- they never pass silently,
## and on Linux a missing shim is still a failure.
preload_shims = host_machine.system() == 'linux'
shim_env = [ 'CYANRIP_PRELOAD_SHIMS=' + (preload_shims ? '1' : '0') ]
shim_deps = []

if preload_shims
## One unreadable sector, for the image rips. An LD_PRELOAD shim, not a test
## of its own: rip_images.py's `bad_sector` scenario rips through it. See the
## file header for why a drive is not needed for this half of "damaged media".
badsector_shim = shared_module('badsector',
    sources: [ 'badsector.c' ],
    name_prefix: '',
    dependencies: [ dependency('dl') ],
)

## A signal at a named moment, for the image rips. Another LD_PRELOAD shim: it
## raises SIGTERM straight after a named line reaches stdout, so a scenario can
## put an interrupt in a window a timer only hits by luck. See its header.
raisesig_shim = shared_module('raisesig',
    sources: [ 'raisesig.c' ],
    name_prefix: '',
    dependencies: [ dependency('dl') ],
)

## An image that reports reading ISRC, as libcdio 2.3.0 and later make every
## image do. The Linux jobs build against 2.1, so without this nothing here
## would notice cyanrip again taking that bit to mean a drive. See its header.
imagecap_shim = shared_module('imagecap',
    sources: [ 'imagecap.c' ],
    name_prefix: '',
    dependencies: [ dependency('dl'), dependency('libcdio') ],
)
## One write to the log that fails, with the writes around it going through,
## so the log on disk is missing a message and nothing else. Review C item 1.3:
## such a log was signed and -Y called it valid. See its header.
losewrite_shim = shared_module('losewrite',
    sources: [ 'losewrite.c' ],
    name_prefix: '',
    dependencies: [ dependency('dl') ],
)
shim_env += [ 'CYANRIP_BADSECTOR_SHIM=' + badsector_shim.full_path(),
              'CYANRIP_RAISESIG_SHIM=' + raisesig_shim.full_path(),
              'CYANRIP_IMAGECAP_SHIM=' + imagecap_shim.full_path(),
              'CYANRIP_LOSEWRITE_SHIM=' + losewrite_shim.full_path() ]
shim_deps = [ badsector_shim, raisesig_shim, imagecap_shim, losewrite_shim ]
endif

json_test = executable('json_test',
    sources: [ 'json.c' ],
    include_directories: [ '../src' ],
    objects: cyanrip_exe.extract_objects([ 'json.c' ]),
    dependencies: unit_test_deps,
)
test('JSON reader', json_test)

## The parsers of data from outside this program, each behind a harness in
## tests/fuzz/ (review C item 3.8): the JSON reader, AccurateRip's response
## and -Y's check of a log. Every build runs each harness over its committed
## seeds and 2000 mutations of each (tests/fuzz/driver.c), so CI's sanitizer
## rows run them under ASan and UBSan. With -Dfuzz=true, and clang, each is
## also built for libFuzzer as fuzz_<name>, which CI's fuzz job runs.
fuzz_harnesses = {
    'json': {
        'sources': [ 'fuzz/fuzz_json.c', '../src/json.c' ],
        'deps': [ dependency('libavutil') ],
        'seeds': files('fuzz/seeds/json/submit-ok.json',
                       'fuzz/seeds/json/error.json',
                       'fuzz/seeds/json/values.json'),
    },
    'accurip': {
        'sources': [ 'fuzz/fuzz_accurip.c' ],
        'deps': unit_test_deps + [ dependency('libcurl') ],
        'seeds': files('fuzz/seeds/accurip/dBAR-014.bin'),
    },
    'log': {
        'sources': [ 'fuzz/fuzz_log.c', '../src/fun512.c' ],
        'deps': [ dependency('libavutil') ],
        'seeds': files('fuzz/seeds/log/no-checksum.txt',
                       'fuzz/seeds/log/mismatch.txt',
                       '../docs/golden-reference.log'),
    },
}
if get_option('fuzz') and cc.get_id() != 'clang'
    error('-Dfuzz=true needs clang, for libFuzzer; this compiler is ' + cc.get_id())
endif
foreach name, h : fuzz_harnesses
    driven = executable('fuzz_' + name + '_seeds',
        sources: h['sources'] + [ 'fuzz/driver.c' ],
        include_directories: [ '../src', 'fuzz' ],
        dependencies: h['deps'],
    )
    test('Fuzz harness, ' + name, driven, args: h['seeds'], timeout: 300)
    if get_option('fuzz')
        executable('fuzz_' + name,
            sources: h['sources'],
            include_directories: [ '../src', 'fuzz' ],
            dependencies: h['deps'],
            c_args: [ '-fsanitize=fuzzer' ],
            link_args: [ '-fsanitize=fuzzer' ],
        )
    endif
endforeach

genopt_test = executable('genopt_test',
    sources: [ 'genopt.c' ],
    include_directories: [ '../src' ],
)
test('Option parsing', genopt_test)

## Integration tests
## =================
## Rip the disc image fixtures with the built binary and verify the
## finished files.
python = import('python').find_installation()
# The suite runs on the Python meson runs on, which the floor above does not
# name; it needs 3.10 too
if not python.language_version().version_compare('>=3.10')
    error('the suite needs Python 3.10 or later, and meson runs on ' +
          python.language_version())
endif

## Zero compiler diagnostics under the flags the build ships. Installed while
## the count was 0, which is the only cheap moment. NOT -Wextra: that set is 22
## and needs its own change. See the tool's docstring for what is excluded and
## for the -fdiagnostics-color trap that made an earlier attempt report a false
## zero.
## The build directory is the one meson is testing, named to the tool: it read
## a fixed build/, so `meson test -C` anywhere else failed as unconfigured or
## gated a stale build/ (review C item 3.3).
test('Compiler diagnostics', python,
    args: [ files('../tools/warn-gate.py'),
            '--build', meson.project_build_root() ],
    timeout: 300,
)
## Which of those diagnostics gate: the ones located in this tree. A flag of
## ours firing in a dependency's header (clang, Homebrew's cdda.h, on CI's
## first macOS run) is listed and not counted.
test('Compiler diagnostics gate only this tree', python,
    args: [ files('warn_gate.py') ])


## Audio checksum mirror
## =====================
## tools/audio-checksums.py reimplements src/checksums.h in Python so a rip's
## files can be checked against a rip's log -- which is how "14/14 bit-perfect
## vs EAC" stopped being somebody's report and became a command.
##
## THIS IS NOT WHAT NOTICES THE TWO DRIFTING, and this comment said it was
## until 2026-09-25. self-test pins the Python against itself: with
## src/checksums.h's v1 sum perturbed and the build green, it exited 0. The
## comparison with the C is the audio_checksums image scenario, which failed 3
## checks on the same build. Found reading our own tests by name, round 27.
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
## Where the golden checks apply: the reference is a byte record of one
## libcdio and one FFmpeg, and both checks say SKIP, naming both sets, on any
## other (CI's macOS job, owner's decision of 2026-10-12). This pins that
## decision, its fail-closed edges, and check-settled counting a 77 as
## unprobed rather than as checked or as stale.
test('Golden reference library set', python,
     args: [ files('golden_libraries.py') ])

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

## Dependency map freshness
## =========================
## sbom.cdx.json (CycloneDX 1.7) and docs/DEPENDENCIES.md are derived from the
## tree: the libraries and minimums from src/meson.build, the programs the tools
## and tests run, the URL literals in src/, CI, the shared seam documents and
## CLAUDE.md's external-bug section. This fails when either file no longer says
## what the tree declares, and the generator refuses outright when a library,
## program or host is used and undescribed. What it MEASURED on the machine
## that generated them -- installed versions, licences confirmed from copyright
## files, the fork point -- is not compared, so CI is not drift.
test('Dependency map is current', python,
     args: [ files('../tools/gen-dependency-map.py'), '--check' ])

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

## Short letters (CLAUDE.md, "Watching upstream")
## ==============================================
## An option this fork adds is long-only: upstream allocates short letters,
## and its b40c1f0 gave -k to --acoustid-key while -k was --stall-secs here.
## Reads upstream's option table at the last upstream commit merged, and
## skips (77), saying what it did not check, where git cannot give it one.
test('Fork options are long-only', python,
     args: [ files('option_letters.py'), cyanrip_exe ])

## CLAUDE.md is loaded whole by every session, so it holds only the rules a
## session needs on every task: 300 lines and 32 KiB, the operator's review of
## 2026-10-19, item 3. Its history is in docs/history/.
test('CLAUDE.md within its cap', python,
     args: [ files('claude_md_cap.py') ])

## And the table the probe publishes, in the shared docs/seam-commands.md §7,
## bounded by its generated-block delimiters so the check never reads prose the
## other side wrote. Without this the table went stale for weeks after the
## probe's grading changed, while every test passed. It also fails when a flag
## the binary's --help lists has no row in §1, §1b or §2, reading each row's
## flag cell only (Platterpus's F8, landed in round 35).
test('Argv table in seam-commands.md', python,
     args: [ files('../tools/probe-argv-surface.py'), '--check',
             files('../docs/seam-commands.md'),
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

## tools/round16-accept.py grades a rig run against round 16's close condition,
## and it was written BEFORE the run so its git history proves the criteria were
## not adjusted to fit the data. S-13 fixes close conditions at lap 1; a checker
## written afterwards is how one quietly moves.
##
## This is the list of ways it could wrongly say a run passed. Every fixture is
## built -- there is no drive here -- so each check is PROVED able to fire
## rather than assumed to be. It also asserts the accepted build ids match
## rig-round16.sh's preflight, because that is one fact described in two files.
test('Round 16 acceptance checker', python, args: [ files('round16_accept.py') ])

## Round 16 lap 7 §H1: our lap 6 told the consumer the contract's one added row
## was in P5. It is in P3. The generator was right; the LABEL was inferred from
## a diff hunk -- "a message inventory row is a P5 row" -- and never checked
## against the document. P3 and P5 are opposites to a consumer: P5 is a fatal
## string they must surface, P3 is unstable wording whose absence from a log
## proves nothing. tools/contract-delta.py derives the section so the inference
## cannot be made again, and this asserts the specific sentence that was wrong.
test('Contract delta names its section', python,
     args: [ files('contract_delta.py') ])

## Round 16 lap 10 §D: our lap 9 §C said "three commits since lap 8" and named
## them in prose. Platterpus derived FIVE from the send pin and NINE from lap
## 8's HANDSHAKE-FROM-COMMIT; two were missing, and one of them corrected the
## Run A block -- the procedure for the one artifact the round waits on. The
## defect is the MISSING RANGE: a count naming no baseline is unfalsifiable, so
## they had to guess two and report both. tools/lap-commits.py derives it, and
## the sharpest check here is the cross-check -- it must reproduce BOTH numbers
## a second, independent implementation got from our own history.
##
## AN EXPLICIT TIMEOUT, because meson's 30 s default is a library default in a
## parallel run -- the shape Platterpus's round 28 lap 2 S21-S22 named from a
## Hypothesis deadline that failed a correct test of theirs at 211 ms. This test
## is the one of ours it fits: fourteen timeouts, every one inside a full suite
## at exactly 30 s, and never slower than ~1 s alone -- except once, 48.4 s wall
## over 0.73 s of CPU, on the first run after the container started. Its own
## run() calls, timed in the next run, came to 0.84 s. So it waits rather than
## works, and a limit with margin lets the next occurrence tell SLOW from HUNG:
## a pass between 30 s and 120 s is a wait, a kill at 120 s is a hang. Every
## other test still on the default was measured at 9.2 s or under.
test('Lap commit list names its range', python,
     args: [ files('lap_commits.py') ],
     timeout: 120)

## A lap body in LSL, the statement language proposed in round 27 lap 6
## (docs/handshake/PROPOSAL-lap-statement-language.md). Every defect either
## side has found in the other's laps was in the prose, never in a header, so
## LSL makes the body fields: a closed set of kinds, each with the fields that
## make it checkable, and references that name a commit. This builds a lap for
## every refusal the spec lists and asserts the message as well as the exit
## code, and it checks every committed lap of ours that declares `LSL: 1`, so
## one cannot be sent malformed.
## An explicit timeout, not meson's 30 s default: this runs a subprocess per
## case, about a hundred of them since LSL 2, and a library default in a parallel run
## is the shape Platterpus's round 28 lap 2 S21-S22 named. 5.9 s alone.
test('Lap statements are well formed', python,
     args: [ files('lap_statements.py') ],
     timeout: 120)

test('Handshake wire conformance', python,
     args: [ files('handshake_wire.py'), meson.project_source_root() ])

## Release gate
## ============
## The "no release while a round is open" rule used to be prose only. This is
## the check that executes it, and these are the ways it could wrongly say yes.
## MEASURED 17.5 s standalone, 2026-09-13, against meson's DEFAULT 30 s -- a
## limit nobody chose. It TIMED OUT at 30.01 s in the full suite the day round 18
## added two lap files, because the gate re-derives every round's digest over
## every lap and that work grows with the record. 1.7x headroom on a parallel
## run is close enough to flake, and a flaky test is worse than none.
##
## This is NOT the same case as `Settled facts` below, and the difference is why
## one gets headroom and the other does not. That one exceeds its limit because
## a SETTLED.md row re-checks a fact about our own parser by calling
## accuraterip.com -- 80.2 s of its 136.8 s -- and raising a timeout over a
## network call inside a gate would keep an unpredictable verdict and only move
## where it misfires. This one is CPU-bound, deterministic, and growing with the
## handshake record exactly as designed.
test('Release gate', python, args: [ files('release_gate.py') ],
     timeout: 120)

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
## In a build that already carries ASan and UBSan -- two of CI's five rows
## -- the sweep skips, saying so: every image scenario here already runs
## under them, and a second instrumented tree would repeat them. The TSan
## row's binary carries neither, so the sweep runs there.
test('Sanitizer sweep', python,
     args: [ files('../tools/sanitize-run.py'),
             '--unless-instrumented', cyanrip_exe.full_path() ],
     depends: cyanrip_exe,
     timeout: 900)
## Valgrind's memcheck over one rip of the basic image (review C item 3.7):
## it sees inside the libraries as built, which no sanitizer instruments.
## Skipped without valgrind or in a sanitized build, except in CI's linux
## (default) row, which installs valgrind and requires it.
test('Rip under memcheck', python,
     args: [ files('valgrind_rip.py'), cyanrip_exe.full_path(),
             meson.current_source_dir() / 'fixtures', get_option('b_sanitize') ],
     depends: cyanrip_exe,
     timeout: 1200)

## Timeout raised from meson's 30 s default: these rows run git and python over
## every lap and the whole record, and it was measured at 27-30 s on a loaded
## machine -- close enough to flake, and a flaky test is worse than none. The
## expensive rows were made cheap in the same change; this is the headroom.
test('Settled facts', python, args: [ files('../tools/check-settled.py') ],
     timeout: 120)

## The black-box sweep
## ==================
## 838 invocations of hostile, malformed and adversarial argv against seven
## invariants -- no death by signal, terminates, a non-zero exit prints
## something, no sanitizer diagnostic, stdin is never read, nothing is written
## outside where the run was told, and a logfile's first line is the fork
## banner. It is the only place the containment invariant is checked at all.
##
## IT MUST RUN ALONE, and that is measured rather than tidiness. Its
## outside-root class compares listings of /, /tmp and $HOME across each
## invocation's window, and that window belongs to the MACHINE: run beside a
## concurrent build it reported 13 containment breaches across 8 invocations,
## every one of them somebody else's file -- GCC assembler temps and another
## process's Python tempfiles. The tool now measures whether attribution is
## possible at all before believing that class, and degrades it to UNPROBED
## when it is not, so a parallel run would not report a false breach; it would
## silently stop checking the one thing only this tool checks.
##
## is_parallel: false is therefore load-bearing. `meson test` runs
## non-parallel tests on their own, which is the condition the class needs.
##
## MEASURED before wiring it in: ~7 minutes for all 838 on this machine, and
## a clean serial run reports no invariant violations. Two classes are
## UNPROBED and say so: I4 needs a sanitizer build, and the three read-only
## filesystem probes cannot bind as root.
##
## Since 2026-09-26 its OWN invocations run four at once, each probe in a
## sandbox cloned for it: 323 s serial, 173 s pooled, with all 838 exit codes
## identical. That is inside the tool and changes nothing above: the suite
## still runs it alone. The per-probe sandbox also found what one shared
## sandbox hid -- four early-failure logs with no banner, because a log an
## earlier probe had left was never "new" again. Fixed in the program at
## `ee0221c`; the tool now checks rewritten logs as well as new ones.
## Which of P5's failure messages does anything here actually assert?
## ================================================================
## PROVIDER-CONTRACT.md P5 is the inventory of every string this program can
## print on a failure path -- the surface a consumer writes its error matching
## against. It is derived from the source, so it cannot describe a binary we do
## not have, and it says nothing at all about whether any of those messages has
## ever been SEEN. The 2026-09-05 audit put it at "~20 of ~128" as a lead;
## measured, it is 7 witnessed of 120, with 6 whose literal prefix is too short
## for a probe to discriminate reported as UNPROBABLE and counted in neither
## column.
##
## IT IS NOT A COVERAGE GATE AND MUST NOT BECOME ONE. Most of P5 needs a real
## drive, a live network or an allocation failure; a check that failed until
## every row had a witness would be red forever, and a permanently red gate is
## one nobody reads. What --gate fails on is the two things that are defects: a
## citation naming a message P5 does not publish, which means the text was
## reworded and the assertion now names something the binary cannot print, and
## the witnessed count falling below its recorded floor.
##
## Both directions are revert-proved. Adding a bogus "Unable to reticulate the
## splines" to a test file exits 1 and names the file; removing it exits 0.
test('P5 message witnesses', python,
     args: [ files('../tools/message-witness.py'), '--gate' ],
     timeout: 120)

## A citation that fills a conversion is citing the message: upstream's test
## asserts `Invalid track naming scheme`, which the binary prints for
## `Invalid %s naming scheme "%s"!`. tests/message_witness.py checks fills()
## both ways, so a reworded message cannot hide behind a conversion.
test('P5 citations fill conversions', python,
     args: [ files('message_witness.py') ])

test('Black-box sweep', python,
     args: [ files('../tools/blackbox.py'), '--binary', cyanrip_exe, '--gate' ],
     is_parallel: false,
     timeout: 1800)

## Reading a delivered bundle
## =========================
## The 2026-09-03 acceptance bundle said its own run FAILED -- report.json
## "ok": false, and five [ FAIL ] lines in its transcript -- and we published
## that it passed. Both files were in our hands and neither was read; the
## filing note that should have exposed the omission was written from memory of
## what was dropped rather than derived from it.
##
## tools/ingest-bundle.py reads the run's verdict BEFORE anything else and
## derives the not-filed list as a set difference. This pins both properties,
## on archives it builds itself -- a test that needs a delivered upload cannot
## run in a clone, and the states that matter (no verdict file at all, a
## passing one, a failing one) are states no single real bundle supplies.
test('Bundle ingest', python, args: [ files('ingest_bundle.py') ])

## tools/take-in-lap.py takes in a peer lap and runs every check that exists
## on it; tools/read-run.py prints what a filed run shows. Both were written on
## 2026-10-13, when a lap's checks and a run's reading were still rebuilt by
## hand each time, and the hand reading of that day's run missed a securing
## pass and a pregap one list left out. The refusals and the report sections
## are checked on a peer repository and logs built here.
test('Lap intake and run reader', python,
     args: [ files('lap_and_run_tools.py'), cyanrip_exe ])

## The owner's rule of 2026-10-12: home folders, the hostname and the owner's
## real name stay out of anything newly committed, through the export and
## filing tools. tests/redaction.py checks tools/redact.py and the two tools
## that use it, with invented names; the -Y case runs on the golden reference,
## a real signed log with a home path in it. tests/personal_details.py checks
## the laps and evidence committed since the rule, and skips (77) where the
## clone cannot tell new from old.
test('Redaction in the filing tools', python,
     args: [ files('redaction.py'), cyanrip_exe ])
test('No personal details in new laps or evidence', python,
     args: [ files('personal_details.py') ])

## HR-2 (PROTOCOL.md v9 §17) moves run evidence to the `evidence` branch.
## tools/evidence.py is the one place that knows where a file is; its test
## runs a whole move on repositories built here, by file:// URL. The readers
## check refuses a new test, tool or SETTLED row that names an evidence path
## (HR-2 point 2) and checks each fixture copy against its source. Files filed
## straight to evidence never pass through a checkout, so their personal-
## details check runs where they are fetched: CI's evidence job, 77 elsewhere.
test('Evidence tool', python, args: [ files('evidence_tool.py') ], timeout: 120)
test('Evidence readers and fixture copies', python,
     args: [ files('evidence_readers.py') ])
test('No personal details in new evidence', python,
     args: [ files('personal_details.py'), '--evidence' ])

## tools/cross-rip.py compares each track's EAC CRC32 across every cyanrip log
## in a bundle. Round 26's reading read logs one at a time and missed a wrong
## track-1 read that only shows beside the other rips of it (their round 26
## lap 5 §B3), and the same wrong read had been filed thirteen days earlier.
## The test asserts both are named, and pins the synthetic directions no real
## bundle supplies: identical reads agree, another offset is not compared, and
## an EAC-format export is not taken for a log.
test('Cross-rip reader', python, args: [ files('cross_rip.py') ])
## Platterpus's round 30 lap 14 S20: a lazy capture before trailing blanks is
## quadratic in a run of blanks. Five of our tools' patterns had it; this
## sweeps tools/ and tests/ for the shape and times the rewritten patterns.
test('Tool patterns are linear', python, args: [ files('tool_patterns.py') ])
## The workflows, as hardened on 2026-10-12: a read-only token by default and
## write only where a job publishes, a timeout on every job, every action at a
## full commit SHA, no ::set-output, upstream's nightly steps confined to
## cyanreg/cyanrip, no expression pasted into a shell script, triggers on
## platterpus-fork, and no main.yml beside upstream's. Actions had never run
## here, so a regression would have shown first in a run with a write token.
test('Workflows are hardened', python, args: [ files('workflows.py') ])
## .github/mingw-build.sh runs only in the Windows job. This sources its
## functions with stubs for the builds and checks that each failure stops it
## (review C item 4.6); skipped without a GNU Bash 4.4 and xargs, as MSYS2 has.
test('Windows build script stops where it fails', python, args: [ files('mingw_build.py') ])
## .claude/hooks/session-start.sh, on scratch repositories, one with its
## config locked: it says it excluded the evidence branch only when git wrote
## the exclusion (review C item 4.7).
test('Session hook says only what it did', python, args: [ files('session_hook.py') ])
## ruff's Pyflakes rules over tools/ and tests/ (review C item 4.3); skipped
## where ruff is not installed, except in CI's linux (released) row.
test('Python lint', python, args: [ files('python_lint.py') ], timeout: 300)
## Each text read, write and subprocess pipe in tools/ and tests/ names its
## encoding, found by the AST (review C item 6.5).
test('Text I/O names its encoding', python, args: [ files('text_encoding.py') ])
## tools/check-commit-subjects.py, which CI's evidence job runs on each
## change's commits (review C item 5.2), on a scratch repository.
test('Commit subject check', python, args: [ files('commit_subjects.py') ])
## tools/tag-release-check.py decides every tag the tag workflow creates, on a
## repository this builds: on platterpus-fork, named by the manifest at that
## commit, ordered by release_seq, never moved. The workflow itself cannot be
## tried out, because what it makes is a tag.
test('Release tag check', python, args: [ files('tag_release.py') ])
## A REPORT, NOT A CHECK. --gaps prints the absent lap numbers and exits 0 by
## design, because one side cannot tell a lost lap from an unused number. It
## was named "Seam record audit", which a green run made read like a passed
## audit of the record. It fails only if the tool itself breaks. The check is
## the inbound-held audit below. Renamed in round 27.
test('Seam gap report', python, args: [ files('../tools/seam-check.py'), '--gaps' ])

## --gaps prints which lap numbers WE are missing and then says, correctly,
## that no check on one side can tell a lost lap from a number nobody used:
## "ask for the other side's enumeration -- that is what it is for."
##
## --held is that advice, taken. Their enumeration has been in every inbound
## lap's HANDSHAKE-INBOUND-HELD since round 9 and no tool had ever read it.
## It checks only the hashes they quote against our lap files -- the field is
## prose by design, and round-14 lap 8 writes "NOT held: your round-14 lap 2"
## in the same sentence shape as everything it does hold, so an extractor
## reading lap numbers out of it would read that one exactly backwards.
##
## It FAILS when a hash they quote does not match our file, which is a §4a
## violation by whichever side edited a sent lap -- and it covers laps sent
## long before we kept any record of sending, because THEIR file is the
## independent artifact.
test('Seam inbound-held audit', python,
     args: [ files('../tools/seam-check.py'), '--held' ])

# From 2.2.1 on, libcdio numbers a CUE sheet's tracks from 1, whatever the
# first one's number is
cue_track_numbers = dependency('libcdio').version().version_compare('< 2.2.1')

rip_scenarios = [
    'info',
    'cli',
    'basic',
    'pregap',
    'mixed',
    'data_track_completed',
    'kept_read_began',
    'trailing',
    'discid',
    'nrg',
    'filters',
    'deemph_with_hdcd',
    'loudness_after_filter',
    'media_tag',
    'tag_keys_in_capitals',
    'golden_reference_matches_a_fresh_rip',
## THE SUITE NEVER CHECKED THE AUDIO AGAINST THE LOG THAT DESCRIBES IT.
## tools/audio-checksums.py reimplements src/checksums.h in Python so a rip
## can be verified by something that is not the C that produced it -- and only
## its `self-test` was wired, which proves the reimplementation has not
## drifted from ITSELF. The 2026-09-05 audit filed the gap as lead (b).
##
## The reason it stayed open was real: `check` decoded through ffmpeg, which
## is absent here, and it died with a traceback rather than saying so. A .pcm
## file IS interleaved s16le stereo, so it is now read rather than decoded,
## and the check runs with no external decoder at all.
    'audio_checksums',
    'contract_line_shapes',
    'album_loudness',
    'contract_covers_log',
    'art',
    'art_extradata',
    'art_local_name',
    'lost_writes',
    'lost_log_line_is_not_signed',
    'acoustid_key_withheld',
    'acoustid',
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
    'status_block_is_current',
    'docs_do_not_contradict_themselves',
    'changelog_names_every_release',
    'encode_failure_reaches_the_log',
    'cache_table_matches_the_transcripts',
    'format_guard',
    'cue_isrc',
    'version_matrix',
    'exit_codes',
    'reference',
    'paranoia',
    'verify_log',
    # Round 16 lap 14 §C: we renamed Platterpus's 2026-09-10 logs when filing
    # them. The bytes survived; the mapping back to the delivered names did not
    # get recorded. Their verify_log_surface.py excluded their OWN EAC exports
    # by NAME -- which worked over their bundle and failed over our filed copy,
    # because `*.eac.log` is a third spelling of one artifact, so 43 lines of
    # their own export were reported as evidence that OUR format had moved.
    # The README now carries the mapping; this asserts it still describes the
    # directory. Renaming is a change to an artifact even when every byte
    # survives.
    'filed_rig_is_mappable',
    # Three versions of STATUS.md's Run A block have been wrong, each found by
    # RUNNING it: one fetched two files and ran a third; one assumed a clone the
    # operator was not standing in; one omitted the grader's clause-1 reference
    # log, which a fresh clone lacks because master is a clean upstream mirror.
    # Three failures of care is a missing check. The required list is derived
    # from the tools' own source.
    'runa_block_is_complete',
    'interrupt',
    'signal_after_last_frame',
    'interrupt_deadlock',
    'cache_probe_only',
    'artifacts_are_tracked',
    'argv_probe_names_what_it_did_not_see',
    'argv_probe_reads_the_record',
    'encoder_option',
    'mutation_exclusions_are_pinned',
    'sanitize',
    'enhanced_cd',
    'contract_diagnostics',
    'diag_repeated_flag',
    'contract_composed',
    'contract_fatal_inventory',
    'curl_timeouts',
    'timestamp_offset',
    'utf8_naming',
    'outdir_is_a_file',
    'consumer_argv',
    'abort_footer',
    'bad_sector',
    'p0_bad_sector',
    'repeat_limit',
    'repeat_limit_keeps_most_agreed',
    'z_extraction_speed',
    'log_values_cannot_forge_a_line',
    'gaps_unknown_pregap',
    'spool_refusal',
    'paranoia_skip',
    'repeat_resets_filter',
    'zr_refusal',
    'probe_runs_open_no_logfile',
    'diag_record_v8',
    'image_reports_isrc',
    'disc_isrc_line',
    'overread_bounded',
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
         env: [ declared_env,
                'CUE_TRACK_NUMBERS=' + (cue_track_numbers ? '1' : '0') ] + shim_env,
         depends: shim_deps,
         suite: 'images',
         timeout: 120)
endforeach
