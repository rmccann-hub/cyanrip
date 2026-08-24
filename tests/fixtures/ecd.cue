REM Enhanced CD (CD-Extra) SHAPE: audio tracks with a TRAILING data track.
REM
REM What this exercises: the branch in cyanrip_main.c that treats a trailing
REM data track as a second session and takes CDEXTRA_SESSION_GAP frames off the
REM last audio track. No other fixture has a data track in last position --
REM mixed.cue puts it first, which is a mixed-mode CD and a different layout.
REM
REM What it does NOT exercise, and this is the point of saying so: a WELL-FORMED
REM Enhanced CD, where the last audio track is longer than the 11400-frame gap.
REM That needs 11400 sectors of audio ahead of the data track -- 26.8 MB of BIN
REM to commit -- so what is here is the case where the gap does NOT fit. That
REM case used to run the LSN negative, hit undefined behaviour in discid.c and
REM publish a garbage TOC at exit 0; it is now refused with a diagnostic. The
REM well-formed path stays unproven by any test and needs a real disc.
FILE "ecd.bin" BINARY
  TRACK 01 AUDIO
    INDEX 01 00:00:00
  TRACK 02 AUDIO
    INDEX 01 00:03:00
  TRACK 03 MODE1/2352
    INDEX 01 00:06:00
