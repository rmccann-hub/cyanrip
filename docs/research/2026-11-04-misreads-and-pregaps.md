# Repeatable misreads and pregaps: what EAC and the others do, and what we should

*Written 2026-11-04 on the owner's word of that day: "We've been chasing this
ctdb and related issue for many rounds and laps now we need to come up with a
solution. Is EAC able to do it? Then so should we, unless they are flawed. If
this requires more research, looking at other open source repos, etc we should
do that."* The owner sent Platterpus the same message. This is our side's
answer. The two research reports it rests on are beside it, each finding
labelled by its source:

- [`2026-11-04-misreads-ar-ctdb.md`](2026-11-04-misreads-ar-ctdb.md): tracks
  3 and 5, AccurateRip, CTDB and repair;
- [`2026-11-04-pregaps.md`](2026-11-04-pregaps.md): track 9's pregap.

Nothing in either was run on a drive, and no code downloaded for them was
executed.

## The answer

**EAC can't do it either, by its own documented algorithm, and neither can
any ripper that keeps a read because reads agree.** Track 5 on our drive reads
`E0036697` the same way time after time. EAC's secure mode without C2 accepts
two identical reads, so on this drive it would very probably keep the same
wrong value. That isn't run, but it follows from EAC's documentation. EAC,
CUERipper, XLD, whipper, morituri, cdparanoia and upstream cyanrip all decide
by agreement. EAC's, cdparanoia's and dBpoweramp's own documents say a
consistent error gets through that way. dBpoweramp's guide puts it plainly:
*"consistent errors exist and in our opinion present more of a problem to
secure ripping than the C2 error pointer detection 'hole'."*

**Three tools do better, in two different ways**, and we can do both:

1. **Use AccurateRip inside the read loop.** dBpoweramp stops a track as soon
   as any pass matches AccurateRip, and can read the next pass at another
   speed. riprip stops re-reading once AccurateRip or CTDB confirm the track.
   Neither needs reads to agree.
2. **Repair after the rip, from CTDB's parity.** CUETools fetches the Reed-
   Solomon parity of the CTDB entry most submitters agree on, corrects the rip
   to it, and checks the result against the entry's whole-disc CRC32. Our track
   5 differs from that entry in 3 samples. That's well inside what the parity
   can fix, if the rest of the disc matches the entry.

**Our own record says the first would already have worked once.** On
2026-10-06 this drive read track 5 as `C96464AB`, which AccurateRip verifies,
and the repeat limit kept `E0036697` by agreement instead
(`docs/rig-2026-10-06-5704062/`). So the disc and drive can give the right
answer. What fails is how we choose which read to keep. Three unrelated
sources now point at the same 3 samples of track 5:
- AccurateRip's frame-450 match, which says same pressing, with the difference
  elsewhere in the track;
- CTDB's majority entry, 3 samples away at 02:24:59;
- our drive's own verified read, `C96464AB`.

**Pregaps are a different problem with a weaker answer.** No tool claims its
pregaps are exact. AccurateRip, CTDB, MusicBrainz and gnudb key on `INDEX 01`
only, so no public database can check a pregap. With gaps appended to the
previous track, a pregap's length changes no checksum. EAC's own page puts its
gap detection within *"2-3 sectors"*. The careful readers (cdrdao's default
scan, redumper, DiscImageCreator, and upstream pull request 153) read raw P-W
sub-channel rather than formatted Q, as ours does, and two of them confirm a
boundary before deciding.

## What we propose

Each item is labelled by who owns it under `docs/OWNERSHIP.md`: the ripper
owns what needs the disc in the drive, Platterpus what can be derived
afterwards. Every ripper item changes drive I/O or the log, so it needs a
hardware run on the BDR-209D, and every log change is handshake material for a
round.

### First, three observations on the rig: no code, operator's time

1. **How often does this drive read track 5 right?** Twenty `-Z`-less reads of
   track 5, and twenty of track 3, at the default speed and at a forced lower
   one. The rate decides whether the AccurateRip stop alone is worth having.
2. **Track 9's sub-channel, raw against formatted.** Read LSN 145560 to 145575
   with READ CD's raw P-W (`001b`) and formatted Q (`010b`), several passes
   with a cache defeat between them. This settles which of two documented
   mechanisms holds: a drive that hands back the previous sector's frame, or an
   MCN or ISRC frame on the boundary sector.
3. **Two other programs on the same disc:** `cdrdao read-toc` and redumper,
   for track 9's pregap, cited as their claims.

### Then the ripper (ours): propose in round 39

- **R1. AccurateRip as a stop and a keep rule**, opt-in, as dBpoweramp does.
  - Each whole-track read is checked against AccurateRip's v2 checksum, or v1
    where the entry has no v2, and the first verified read ends the track.
  - When AccurateRip has the disc, agreement among unverified reads doesn't end
    the track until the read budget is spent. At the limit a verified read is
    kept over an outvoted one, which `--prefer-accuraterip-match` already does.
  - The log names the rule that chose the read.
  - It would have kept `C96464AB` on 2026-10-06. Cost is low: AccurateRip is
    fetched before the rip and its checksums are computed per read already.
- **R2. Every distinct read in the log and the record**: checksum, how many
  reads gave it, AccurateRip's answer, and paranoia's jitter-fix count. Option:
  keep each alternate's audio, so Platterpus can choose among them afterwards.
- **R3. A speed change between passes** when reads disagree or AccurateRip
  fails, if the first observation shows it helps on this drive.
- **R4. Pregap reads** that need nothing from the rig first:
  - keep `94 or 95 frames (undecided)` and add why the sector is undecided,
    whether no frame of its own, a failed CRC, or a mode-2/3 frame;
  - cache defeat between retries, now a commented-out TODO
    (`src/pregap.c:390-392`).
  Raw P-W reads, reading runs of sectors, and a two-observation confirmation
  rule follow if the second observation supports them.
- **Later, R5. Sector-level re-reads.** With CRCs per block of every read, re-
  read only the disputed sectors, and accept a combination only when
  AccurateRip then verifies the track. No established ripper documents this,
  and every combination tried adds a little false-match risk, so it waits for
  R1 and R2's results.

### And Platterpus (theirs): for them to decide

- **A1. CTDB repair**, with provenance: never from a confidence-1 entry; keep
  the original; record each repaired sample's position and the entry used.
  On track 5 it is expected to give back `C96464AB`, which AccurateRip and our
  own drive would then confirm independently. No repair implementation exists
  outside C# (`ctdb-cli` runs it on Linux under .NET). The code's licence is
  unclear between GPL-2.0-or-later and LGPL, so a port needs the author's word
  or GPL terms.
- **A2. Choose among alternates** the ripper kept, once R2 keeps them.

## What we got wrong on the way

- **Our `-Z` described wrongly.** We described `-Z 2` to the researchers as "until 2 reads agree". It
  is 3 reads agreeing: the read in hand and 2 before it
  (`src/cyanrip_main.c:1906`), as every log's `converged after 3 reads`
  says.
- **No reading plan for the `.29` run.** We wrote none before the run
  arrived, and the procedure asks for one.
- **The lower-speed request went unmet.** The 2026-11-03 reading asked for track 3 at a forced lower
  speed, and no rip of the 2026-11-04 run did it. The first observation above
  asks again.
