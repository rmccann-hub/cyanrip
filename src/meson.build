build_opts = [
    '-D_ISOC11_SOURCE', '-D_XOPEN_SOURCE=700', '-U__STRICT_ANSI__',

    # Warnings
    '-Wundef', '-Wmissing-prototypes', '-Wshadow', '-Wparentheses',
    '-Wpointer-arith', '-Wno-pointer-sign',

    # Warnings to treat as errors
    '-Werror=implicit-function-declaration',

    # cyanrip_log() and friends carry av_printf_format() so that -Wformat
    # applies to them at all -- until it was added, not one format string in
    # the program had ever been checked. An error rather than a warning
    # because the output is an archival record: a mismatch here is a wrong
    # number, or adjacent process memory, printed into a file nobody can
    # re-take a measurement for.
    '-Werror=format', '-Werror=format-extra-args',

    # The rest of -Wformat's checks: a non-literal format, %n, and a format
    # with no arguments to check (review C item 3.9)
    '-Wformat=2',
]

#fix for MinGW32
if host_machine.system() == 'windows' and cc.sizeof('void*') == 4
  build_opts += '-D__MINGW_USE_VC2005_COMPAT'
endif

# Hardening, asked for here rather than left to the compiler's vendor:
# Ubuntu's GCC supplies these, MinGW's and macOS's Clang do not (review C item
# 3.5; the set is the coding skill's c-build module at claude-code-skills
# 951bf00). Each must link, not only compile: a static MinGW link can lack
# __stack_chk_fail. FORTIFY needs optimisation, sanitizers do not support it,
# and the Windows build sets it to 0 itself (.github/mingw-build.sh); -U first,
# so a vendor's own level is replaced rather than redefined.
hardening = [ '-fstack-protector-strong', '-fstack-clash-protection',
              '-fcf-protection=full' ]
if get_option('b_sanitize') == 'none' and \
   get_option('optimization') not in [ '0', 'plain' ] and \
   host_machine.system() != 'windows'
  hardening += [ '-U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=3' ]
endif
# Clang only warns about a flag it ignores on the target, as Apple's does with
# -fstack-clash-protection on arm64, so a link check alone let that one in and
# every compile on macOS then warned; checked as an error, it is left out. GCC
# has no such warning, and is checked as before.
strict_check = cc.get_supported_arguments('-Werror=unused-command-line-argument')
foreach flag : hardening
  if cc.links('int main(int c, char **v) { char b[64]; b[c & 63] = 0; return v[0][0] + b[1]; }',
              args: strict_check + flag.split(), name: flag)
    build_opts += flag.split()
  endif
endforeach
add_project_link_arguments(
    cc.get_supported_link_arguments('-Wl,-z,relro', '-Wl,-z,now',
                                    '-Wl,-z,noexecstack'),
    language: 'c')

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
    # static: a static curl with Schannel needs secur32 and crypt32 from
    # its Libs.private, which only a static lookup reads (review C item 1.5)
    dependency('libcurl', version: '>=7.66.0', static: static_build),

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
# Round 10 §J1(b). Built as a list rather than a ternary so the flag is either
# present or absent: passing a placeholder like '--no-op' to make both branches
# the same shape would be an argument the tool must then accept, and a tool that
# accepts a meaningless flag will one day accept a misspelt meaningful one.
handshake_declare_args = []
if get_option('declare_released')
    handshake_declare_args += '--declare-released'
endif

handshake_state_h = custom_target('handshake_state.h',
    output: 'handshake_state.h',
    build_always_stale: true,
    command: [ python3,
               meson.project_source_root() / 'tools/gen-handshake-state.py',
               handshake_declare_args,
               '@OUTPUT@' ],
    build_by_default: true,
)

sources = [
    'cyanrip_encode.c',
    'cyanrip_log.c',
    'log_escape.c',
    'cyanrip_main.c',
    'naming.c',
    'fun512.c',
    'utils.c',

    'fifo_frame.c',
    'fifo_packet.c',

    'discid.c',
    'musicbrainz.c',
    'qrcode.c',
    'coverart.c',
    'accurip.c',
    'acoustid.c',
    'json.c',

    'cue_writer.c',

    'cdtext.c',
    'cache_probe.c',
    'drive_caps.c',
    'stall_watchdog.c',
    'diagnostics.c',

    'pregap.c',

    # Handshake state, compiled in so a rip can report whether it came from a
    # mutually-verified build or a mid-round working tree. Regenerated whenever
    # a round file changes, so it cannot go stale against the record.
    handshake_state_h,

    # Version
    # A9 (Platterpus, round 7): mark a dirty tree in the build tag. Two golden
    # references have carried a banner naming a commit three behind their stated
    # pin. Both were provable from content so nothing was lost -- but a stale
    # banner on a reference generated from a build that still has the defect is
    # the one failure mode that looks like success.
    # No .git (a source tarball) used to land here as "-dirty" with an EMPTY
    # sha: git rev-parse printed nothing, git diff failed, and the sh -c still
    # exited 0 -- so meson's fallback never fired and the banner read
    # "platterpus-fork-g-dirty". That names no build and asserts a modification
    # that did not happen, permanently, in every logfile it writes.
    #
    # git archive substitutes the commit into src/archive-version.txt via
    # .gitattributes export-subst, so an archive can still name itself. In a
    # working tree that file still holds the literal placeholder, which starts
    # with '$' and so fails the hex test below.
    vcs_tag(command: ['sh', '-c',
                      'cd ' + meson.project_source_root() +
                      ''' && if git rev-parse --short HEAD >/dev/null 2>&1; then
                             printf %s "$(git rev-parse --short HEAD)$(git diff --quiet HEAD || printf -- -dirty)"
                           else
                             a=$(cat src/archive-version.txt 2>/dev/null | tr -d " \n")
                             case "$a" in
                               [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) printf %s "$a" ;;
                               *) printf %s "unknown" ;;
                             esac
                           fi'''],
                      input: 'version.c.in', output: 'version.c',
                      fallback: 'release')
]

# Optional, for printing MusicBrainz submission URLs as QR codes
qrencode = dependency('libqrencode', version: '>= 4.0', required: false,
                      static: static_build)
if qrencode.found()
    conf.set('HAVE_QRENCODE', 1)
    dependencies += qrencode
else
    message('libqrencode not found, MusicBrainz URLs won\'t be printed as QR codes')
endif

# Optional, for AcoustID fingerprinting
chromaprint = dependency('libchromaprint', version: '>= 1.4', required: false,
                         static: static_build)
if chromaprint.found()
    conf.set('HAVE_CHROMAPRINT', 1)
    dependencies += chromaprint
else
    message('libchromaprint not found, tracks won\'t be fingerprinted for AcoustID')
endif

# Check for wmain support (Windows/MinGW)
if cc.links('int wmain() { return 0; }', args: '-municode')
     conf.set('HAVE_WMAIN', 1)
     build_opts += '-municode'
endif

add_project_arguments(build_opts, language: 'c')

cyanrip_exe = executable('cyanrip',
    install: true,
    sources: sources,
    dependencies: dependencies,
)
