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
