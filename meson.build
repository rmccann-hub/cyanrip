project('cyanrip', 'c',
    license: 'LGPL2.1+',
    default_options: [ 'buildtype=debugoptimized', 'c_std=c99', 'warning_level=1' ],
    # Upstream's version verbatim, with the fork release appended as SemVer
    # build metadata. The base moved rc1 -> rc2 because we merged upstream's
    # 4f28cf0; only upstream may change that half, and it changes exactly when
    # we sync. `+platterpus.N` is ours and is the only number we advance.
    #
    # Bumped to .7 here rather than at release time on purpose: CLAUDE.md's
    # release plan says to choose the RELEASED COMMIT after every derived
    # artifact agrees with the version, never at the bump. Bumping first is what
    # makes that possible -- +platterpus.5 was announced at a commit that failed
    # 2 of 33 from a fresh clone precisely because the two were done together.
    # Nothing here claims to be a release: `declare_released` defaults false and
    # the Handshake: line says so in every log this build writes.
    version: '0.9.4-rc2+platterpus.7',
    meson_version: '>=0.53.0',
)

conf = configuration_data()

conf.set_quoted('PROJECT_NAME', meson.project_name())
conf.set_quoted('PROJECT_VERSION_STRING', meson.project_version())

# Identifies this fork in every banner it prints, and remains the reliable
# answer to "is this the fork?".
#
# Version scheme: upstream's number, verbatim, plus our release as SemVer build
# metadata. Upstream is at 0.9.4-rc1 and has cut no 0.9.4 tag, so this build is
# "upstream's 0.9.4-rc1, fork release 3".
#
# Releases r1 and r2 carried upstream's number with nothing appended, which made
# two fork builds indistinguishable by version. The obvious fix -- advance the
# rc number ourselves, 0.9.4-rc2, -rc3 -- was tried and reverted before it
# shipped, because it mints identifiers in upstream's namespace: nothing stops
# upstream tagging its own 0.9.4-rc3, and then two different trees answer to one
# string. "rc3 is unambiguously ours" was true the day it was written and one
# upstream tag away from being false. A `+platterpus.N` suffix cannot collide,
# because upstream will never mint one.
#
# It also leaves exactly one number to track: fork release N appears once, here.
# There is no separate "r2 vs rc1" to reconcile.
#
# Still true, and worth stating: PROJECT_FORK_ID is the only thing that answers
# "fork or upstream?" for a consumer that parses only the leading version
# number. Match on PROJECT_FORK_ID, or on the `+platterpus.` suffix -- never on
# `0.9.4-rc1` alone, which upstream also answers to.
conf.set_quoted('PROJECT_FORK_ID', 'platterpus-fork')

version_split = meson.project_version().split('.')
ver_major = version_split[0]
ver_minor = version_split[1]
ver_micro = version_split[2]

conf.set('PROJECT_VERSION_MAJOR', ver_major)
conf.set('PROJECT_VERSION_MINOR', ver_minor)
conf.set('PROJECT_VERSION_MICRO', ver_micro)
if host_machine.endian() == 'big'
    conf.set('CONFIG_BIG_ENDIAN', 1)
else
    conf.set('CONFIG_BIG_ENDIAN', 0)
endif

cc = meson.get_compiler('c')

subdir('src')
subdir('tests')

install_data(
    'com.github.cyanreg.cyanrip.metainfo.xml',
    install_dir: get_option('datadir') / 'metainfo',
)

configure_file(
    output: 'config.h',
    configuration: conf,
)
