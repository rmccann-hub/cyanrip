build_opts = [
    '-D_ISOC11_SOURCE', '-D_XOPEN_SOURCE=700', '-U__STRICT_ANSI__',

    # Warnings
    '-Wundef', '-Wmissing-prototypes', '-Wshadow', '-Wparentheses',
    '-Wpointer-arith', '-Wno-pointer-sign',

    # Warnings to treat as errors
    '-Werror=implicit-function-declaration',
]

#fix for MinGW32
if host_machine.system() == 'windows' and cc.sizeof('void*') == 4
  build_opts += '-D__MINGW_USE_VC2005_COMPAT'
endif

static_build = get_option('default_library') == 'static'

# Required dependencies
dependencies = [
    # ffmpeg libs
    dependency('libavcodec', version: '>= 59.24.100'),
    dependency('libavformat', version: '>= 58.13.100'),
    dependency('libswresample', version: '>= 4.5.100'),
    dependency('libavfilter', version: '>= 7.16.100'),
    dependency('libavutil', version: '>= 57.25.100'),

    # other dependencies
    dependency('libcdio', version: '>= 2.0'),
    dependency('libcdio_paranoia', version: '>= 10.2'),
    dependency('libmusicbrainz5', version: '>= 5.1', static: static_build),
    dependency('libcurl', version: '>=7.66.0'),

    # misc
    dependency('threads'),
    cc.find_library('m', required : true),
]

# Base files
# Regenerated on every build, because the header must notice a round file being
# *added* and not only one it already knew about changing. A configure-time glob
# and a depfile both enumerate what existed last time, so a new lap file appears
# and the header goes on describing the previous one -- this shipped a binary
# reporting "lap 2" from a tree whose latest lap was 3.
#
# The generator rewrites the file only when its content changes, so running
# always costs a python invocation rather than a rebuild of everything that
# includes it.
handshake_state_h = custom_target('handshake_state.h',
    output: 'handshake_state.h',
    build_always_stale: true,
    command: [ find_program('python3'),
               meson.project_source_root() / 'tools/gen-handshake-state.py',
               '@OUTPUT@' ],
    build_by_default: true,
)

sources = [
    'cyanrip_encode.c',
    'cyanrip_log.c',
    'cyanrip_main.c',
    'naming.c',
    'fun512.c',
    'utils.c',

    'fifo_frame.c',
    'fifo_packet.c',

    'discid.c',
    'musicbrainz.c',
    'coverart.c',
    'accurip.c',

    'cue_writer.c',

    'cdtext.c',
    'cache_probe.c',
    'stall_watchdog.c',

    'pregap.c',

    # Handshake state, compiled in so a rip can report whether it came from a
    # mutually-verified build or a mid-round working tree. Regenerated whenever
    # a round file changes, so it cannot go stale against the record.
    handshake_state_h,

    # Version
    vcs_tag(command: ['git', 'rev-parse', '--short', 'HEAD'],
                      input: 'version.c.in', output: 'version.c',
                      fallback: 'release')
]

# Check for wmain support (Windows/MinGW)
if cc.links('int wmain() { return 0; }', args: '-municode')
     conf.set('HAVE_WMAIN', 1)
     build_opts += '-municode'
endif

add_global_arguments(build_opts, language: 'c')

cyanrip_exe = executable('cyanrip',
    install: true,
    sources: sources,
    dependencies: dependencies,
)
