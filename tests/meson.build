## Unit tests
## ==========
## Built from the objects they test, avtransport-style.
unit_test_deps = [
    dependency('libavutil'),
    dependency('libavcodec'),
    dependency('libcdio'),
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

## Release gate
## ============
## The "no release while a round is open" rule used to be prose only. This is
## the check that executes it, and these are the ways it could wrongly say yes.
test('Release gate', python, args: [ files('release_gate.py') ])


rip_scenarios = [
    'info',
    'cli',
    'basic',
    'pregap',
    'mixed',
    'nrg',
    'filters',
    'art',
    'cue_only',
    'errors',
    'cdtext',
    'reporting',
    'duration',
    'handshake',
    'early_log',
    'diagnostics',
    'contract_build',
    'cue_isrc',
    'version_matrix',
    'exit_codes',
    'reference',
    'paranoia',
    'verify_log',
]

foreach s : rip_scenarios
    test(s, python,
         args: [ files('rip_images.py'), cyanrip_exe,
                 meson.current_source_dir() / 'fixtures', s ],
         suite: 'images',
         timeout: 120)
endforeach
