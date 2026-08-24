REM Enhanced CD (CD-Extra) SHAPE: audio tracks with a TRAILING data track.
REM
REM What this exercises: the branch in cyanrip_main.c that treats a trailing
REM data track as a second session and takes CDEXTRA_SESSION_GAP frames off the
REM last audio track. No other fixture has a data track in last position --
REM mixed.cue puts it first, which is a mixed-mode CD and a different layout.
REM
REM This is the disc whose gap does NOT fit. That case used to run the LSN
REM negative, hit undefined behaviour in discid.c and publish a garbage TOC at
REM exit 0; it is now refused with a diagnostic, and this fixture pins that.
REM
REM The WELL-FORMED disc -- last audio track longer than the 11400-frame gap --
REM is covered too, and is not here: it needs 29.6 MB of BIN, so the
REM enhanced_cd scenario builds it in its temp workdir instead of committing
REM it. This comment used to say that path "needs a real disc". It does not.
REM
REM What still needs a real disc is whether 11400 is the right number to remove
REM from a PRESSED CD-Extra disc. On an image the data track starts straight
REM after the audio, so the gap comes out of real audio bytes; what libcdio
REM reports for a physical two-session TOC is not knowable from here.
FILE "ecd.bin" BINARY
  TRACK 01 AUDIO
    INDEX 01 00:00:00
  TRACK 02 AUDIO
    INDEX 01 00:03:00
  TRACK 03 MODE1/2352
    INDEX 01 00:06:00
