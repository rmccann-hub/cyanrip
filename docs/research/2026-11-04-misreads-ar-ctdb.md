# Consistent misreads, AccurateRip and CTDB: what other rippers do

Research for the fork's read-strategy and Platterpus's post-rip design. Everything here was read on
2026-11-04. Source code was read at the commits in the table under *How to read this report*.
Nothing in this report was run against a drive.

## Answer

None of the established rippers can tell a read that is wrong the same way every time from a
correct one by re-reading. EAC, CUERipper, XLD, whipper, morituri, cdparanoia and upstream cyanrip
all keep data because reads agree, and EAC's, cdparanoia's and Spoon's own documents say so.
Two tools use a database inside the read loop. dBpoweramp stops a track as soon as any pass
matches AccurateRip (AR). riprip stops re-reading a track once AR or CTDB confirm it. Neither
repairs anything. Only CUETools repairs, and it does so after the rip, from CTDB parity. The
parity is a Reed-Solomon code over 16-bit words laid out in 10-sector columns. It corrects up to
`npar/2` words in each column, so our track 5 difference (3 words in one place) is well inside its
limit, if the rest of the disc matches the majority entry. AR's frame-450 checksum covers one
sector, about 6 s into the track. A frame-450 match at our offset, with no whole-track match, says
our alignment and pressing agree with the database and the difference lies elsewhere in the
track. CTDB places that difference at 02:24:59, and the drive once returned the AR-verified
`C96464AB`. EAC's secure mode without C2 would probably keep the same wrong value on this
drive, going by its documented algorithm (not run). For the fork, the ripper could do what
dBpoweramp does: test each read against AR, keep a verified read even when it is outvoted, and
change speed between passes. For Platterpus, the app could do what CUETools does and repair from
CTDB parity. I found no implementation of CTDB repair outside C#. **Corrected the same day:**
Platterpus's research found `cdverify`, a native Rust one (see *Implementations outside C#*).

## How to read this report

Each finding is tagged by the kind of source behind it:

- **[doc]** the vendor's or author's own documentation;
- **[src]** source code, cited as `repo@commit:path:line`;
- **[vendor test]** a test published by a vendor about its own product;
- **[wiki]** the Hydrogenaudio Knowledgebase, which the community edits;
- **[forum]** a forum post, which is one person's report.

**Not established** means I looked and could not find a source.

| Repository | Commit read | Date of commit |
|---|---|---|
| `gchudov/cuetools.net` | `f2ec33486c23` | 2026-09-05 |
| `cyanreg/cyanrip` (upstream) | `648b1dddd265` | 2026-10-26 |
| `whipper-team/whipper` | `71251a0b86dc` | 2026-02-17 |
| `thomasvs/morituri` | `135b2f7bf277` | 2015-11-09 |
| `Blobfolio/riprip` | `f25123b3fac5` | 2026-10-20 |
| `Blobfolio/cdtoc` | `93a5666fb5b7` | 2026-10-01 |
| `rocky/libcdio-paranoia` | `384f4dac7e21` | 2026-06-12 |
| `bmwalters/python-cuetoolsdb` | `5b6ce15fc866` | 2022-07-03 |
| `Masterisk-F/ctdb-cli` | `627d2daae63d` | 2026-05-09 |

## 1. AccurateRip's frame-450 checksum

### What it is

- **[doc]** Spoon, AccurateRip's author, describes it in the reference post on the AR algorithm
  (dBpoweramp forum, 2010-02-16): *"The offset CRC is a drive offset finding CRC, it is an
  AccurateRip CRC calculation 450 frames in and is calculated with one frames data. This can be
  used when offset adjusted for the drive to find the matching CRCs of other possible pressings,
  finding their offset. ... The maximum offset can be +-5 frames"*. In the record layout the field
  is `DWORD OffsetFindCRC; // AccurateRip Track Offset finding CRC (can be ignored)`, next to
  `Confidence` ("200 = over 200") and `TrackCRC`. Each database entry has one 9-byte record per
  track: confidence, track checksum and frame-450 checksum. There is no separate confidence for
  the frame-450 value.
- **[src]** The samples covered: the v1-style sum `sample × multiplier` over the 588 stereo samples
  of sector 450 of the track, counted from 0. Those are samples 264,600 to 265,187, about 6.0 s
  in, with multipliers 1 to 588.
  - Upstream cyanrip computes it in `cyanrip@648b1dd:src/checksums.h:74-78`.
  - CUETools computes it, at any offset, in
    `cuetools.net@f2ec334:CUETools.AccurateRip/AccurateRip.cs:168-175`. To allow ±5 sectors
    of offset, it keeps running sums for sectors 445 to 455 (`AccurateRip.cs:622`).
- **[src]** Implementations use the field in different ways:
  - **CUETools** counts a frame-450-only match as a "partial". It still prints the track as
    `No match` and uses partials only to decide which other offsets to list
    (`AccurateRip.cs:1003-1013` and `1081-1092`).
  - **Upstream cyanrip** uses frame 450 for its drive-offset search, `-f`
    (`src/cyanrip_main.c:565-571`). In the log it prints `Accurip 450: ... (matches Accurip DB,
    confidence N, track is partially accurately ripped)` (`src/cyanrip_log.c:176-190`). The `N` it
    prints is the whole-track confidence of the first entry whose frame-450 field matches
    (`src/accurip.c:257-271`). It is not a count of frame-450 matches.
  - **XLD** reads it to detect pressings. Its version history for 2010-12-08 says: *"Now XLD uses
    offset finding CRC for detecting different pressings"* **[doc]**.
  - **whipper**, **morituri** and **cdtoc** (used by riprip) skip the field:
    `whipper@71251a0:whipper/common/accurip.py:72-76`,
    `morituri@135b2f7:morituri/common/accurip.py:139-143` and
    `cdtoc@93a5666:src/accuraterip.rs:305-330`.
- **Why sector 450 was chosen: not established.** No source gives the reason. Implementations
  search ±5 sectors around it, and upstream cyanrip skips tracks shorter than 450 sectors plus
  the search range.
- **Whether v2 entries' frame-450 field uses the v1 formula: not established.** Spoon says v2
  checksums sit in the database "side by side with the old ones ... (appear as a different
  pressing)" **[doc]**, but says nothing about their frame-450 field.

### What "frame 450 matches, whole track not found" means

The frame-450 checksum covers 588 of a track's samples, about 0.2% of a 5-minute track. A match
proves only that those 588 samples match an entry at the alignment the match was found at.

- **Different pressing.** In AR's sense a pressing is the same audio at a different offset
  ([wiki] AccurateRip). An offset shifts every sample, so a different pressing matches frame 450
  only at a shifted position, which is how frame 450 finds pressings. Upstream cyanrip computes
  the frame-450 checksum only at the alignment it ripped at, which for us is drive offset +667
  (`src/checksums.h:74-78`). A match in that log line is therefore a match at shift 0, which means
  our alignment equals the entry's. I did not read the fork's code to confirm it does the same.
  dBpoweramp's guide adds a whole-disc test: *"If all tracks dis-agree with AccurateRip then it is
  likely your CD is a different pressing"* [doc]. A pressing difference affects every track, not
  one.
- **Same pressing, data differs elsewhere in the track.** This is the reading that fits a shift-0
  frame-450 match together with a whole-track mismatch. The other case is a different master with
  the same TOC that is identical in sector 450. That case can't be ruled out from AR alone.
  Gregory Chudov, who wrote CUETools, describes seeing it on popular discs: *"My guess is that the
  CD masters slightly differ"* [forum, Hydrogenaudio topic 94318, 2012].
- **For our track 5,** three independent artifacts point to the same-pressing reading:
  1. the frame-450 match at shift 0;
  2. CTDB's majority entry, which differs from our rip only in 3 samples, at track time
     `02:24:59`, about sector 10,859 of the track and far from sector 450;
  3. the drive's own read of 2026-10-06, `C96464AB`, which AR verifies.

  A different master would not let this drive produce the majority value. That holds unless the
  2026-10-06 read was itself an error that collided with an AR checksum, which has a chance on
  the order of 2⁻³² per entry.
- **For our track 3,** the same reasoning applies. Each wrong read matches AR only on frame 450,
  while `59D352DD` verifies.

One AR weakness matters for the options below. The v1 checksum drops part of the right channel:
*"about 3% of the audio data is not counted in the checksum at all ... half of the right-channel
samples are treated as if they're missing anywhere from 1 bit to all 16 bits"* [wiki]. A small
error can therefore leave the v1 checksum unchanged at some positions. v2 adds the high half of
each product, which v1 drops (Spoon's v2 addendum, 2010-03-29) [doc]. The same wiki calls the size
of v2's improvement "suspect", so a v2 match is the stronger of the two, not a proven complete one.

## 2. Exact Audio Copy

### What it does

- **[doc] Secure mode** (exactaudiocopy.de, *Extraction technology*): *"In secure mode this program
  either reads every audio sector at least twice or rely on extended error information ... If an
  error occurs (read or sync error), the program keeps on reading this sector, until eight of 16
  retries are identical, but at maximum one, three or five times (according to the selected error
  recovery quality) these 16 retries are read. So, in the worst case, bad sectors are read up to 82
  times!"*
  - Caching: *"When drives cache audio data, every sector read will be read from the drives cache
    and is that way always identical ... In newer versions it will overread sectors, so that the
    cache contains sectors from a position elsewhere on the CD."*
  - The Hydrogenaudio wiki adds that EAC "continues reading the entire batch of 16, even if it has
    already obtained 8 identical reads" (*EAC Options*) [wiki].
- **[doc] C2** (EAC FAQ): *"some drives do not report these errors correctly, so you should test
  it thoroughly before trusting the results."* The FAQ answers a report of a gap that EAC missed
  with C2 on: *"It seems that C2 is not correctly implemented in some drives. To be on the safe
  side, you should turn off the C2 error correction."*
- **[doc] Test & Copy** (EAC FAQ): *"by comparing the CRC values you could be quite sure that both
  reads resulted in the same file."* It compares two whole-track passes, which is the same test as
  our `-Z` agreement.
- **[doc] AccurateRip** (exactaudiocopy.de, *AccurateRip*): once a drive is configured, EAC *"will
  automatically use the determined offset and ask the AccurateRip database for result comparison
  after extracting a CD."* AR is a check made after extraction. EAC's documents describe no step
  where AR decides which read to keep.
- **[wiki] *EAC Drive Options*:** with the C2 option on, EAC "will not re-read and try to get
  consistent data from sectors which the drive reports as being error-free". On burst mode: "When
  used in conjunction with AccurateRip ... burst mode is completely secure", and it is "handy for
  discs that trigger re-reading in secure mode but cannot be ripped accurately".
- **Speed.** "Allow speed reduction during extraction" is described in a third-party guide as
  "EAC is able to reduce the speed automatically when a read error occurs" (roozster.info, *EAC*).
  EAC's own documents don't describe it. It is triggered by read errors, not by agreement on a
  value.
- **[doc] A consistent wrong value is a known case.** The EAC FAQ answers a sync error "always in
  the same spot": *"Some Toshiba drives have a firmware bug returning wrong data on special
  positions of every CD."*

### Would EAC produce `E0036697` on this drive?

Probably, yes. This is not established, because EAC has not been run on the BDR-209D.

- The drive reports no C2, so EAC would read each sector twice and compare.
- Most of our reads of track 5 return `E0036697`, so both of EAC's reads would usually agree on
  it, and EAC would accept the value without re-reading.
- In a rare pass where one read is right and one wrong, EAC re-reads 16 times and keeps a value
  that 8 of them share. Going by how rarely this drive returns the right value, the wrong value
  is expected to win.
- EAC would then report the track as "cannot be verified as accurate". With the CTDB plugin it
  would print the same `Differs in 3 samples` line we see.
- EAC's read pattern differs from paranoia's: its own read command, block sizes and cache
  overread. Only a run on this drive settles the question.

**Is EAC flawed, or does it have a mechanism we lack?** Neither. It has the same limit as every
agreement-based ripper, and its own documents admit it. For this case it has nothing we lack:
reading twice, re-reading on disagreement and cache defeat by overread are all present in some
form in the paranoia path. Illustrate (dBpoweramp's maker) puts it this way [vendor test,
cd-ripper.com, undated, tested EAC 0.95b4 against dBpoweramp R12]: *"Without C2 error pointers
EAC rips, then re-rips and compares - should an error be duplicated in both reads it will pass
through undetected."* In the same test, EAC without C2 on a Plextor PX-708A logged "Track 2 ...
Track Quality 99.9% AccurateRip: Inaccurate (confidence 19)" with no read error reported.

## 3. dBpoweramp

- **[doc] Consistent errors** (*Spoon's Audio Guide: CD Ripping*): *"CD is read twice, if a
  section contains an error it will likely return different errors, so can be detected. This is
  true mostly but not always, consistent errors exist and in our opinion present more of a problem
  to secure ripping than the C2 error pointer detection 'hole'. As mentioned AccurateRip helps
  enormously with secure ripping, a CD rip is compared to an independently ripped disc (different
  drive, different CD - no 2 discs would have the same scratch)."* On C2: *"even the best
  implementation can still let through 3% or more errors"*.
- **[vendor test] AR as a stop condition** (cd-ripper.com, *Secure ripper*): *"A new strategy is to
  rip in complete passes (AccurateRip is able to jump in and stop a rip after any pass it if
  agrees with AccurateRip)."* And: *"With no C2, there are always 2 passes after which a
  cross-check is done against AccurateRip to determine if elements in each of the pass were
  correct."* The page doesn't define "elements of each pass". **Whether dBpoweramp combines parts
  of different passes to reach an AR match is not established.** The same page says dBpoweramp
  "implemented routines to try to detect interpolation many drives do when there is an error", and
  doesn't describe them.
- **[forum]** An unnamed reply in a 2017 dBpoweramp forum thread on a Pioneer BDR-XD05 says: "If
  AccurateRip verifies it will be 1 pass, if the data is such that it does not verify then a 2nd
  pass is needed". Published logs show the stop working: `AccurateRip: Accurate (confidence 4)
  [Pass 1]`.
- **[doc] Settings** (dBpoweramp help, *CD Ripper: Advanced Options*; *CD Ripper Setup Guide*):
  - **Pass 2 speed.** *"Pass 2 Limit Drive Speed (not used if c2 is enabled) on certain drives
    reading at a different speed is able to detect more errors."*
  - **Ultra Secure.** It *"extends the normal 2 pass reading to a programmable number of passes"*.
    The recommended passes for a drive without C2 are Minimum 3, Maximum 6, End after 2 in the
    help, and Minimum 2, Maximum 4, End after 2 in the setup guide.
  - **Individual bad frames.** *"Maximum Re-Reads ... Without good c2 support (or no c2) 50 has to
    be the maximum (otherwise the chance of getting matching errors is high)."* The setup guide:
    *"Without C2 support it is not recommended that this value be increased, as there is more of
    a chance of a consistent error getting through ripping."*
  - **Cache.** A default of 1024 KB is read to defeat the cache, and FUA invalidation is offered
    for some Plextor drives.
  - **AR-driven marking.** *"It is also to mark tracks which have not passed an AccurateRip
    verification as error."* Re-rip options appear *"if the CRC calculated for each track was
    different on a re-rip (a sure sign one of the rips had an error)"*.
  - **Cross-pressing.** *"Cross-Pressing Verification will use the data from identical CDs to
    yours (which have a different pressing offset) to also verify with AccurateRip."*
- **[forum] Speed variation in practice.** Posted logs show the setting lines `Pass 2 Drive Speed:
  4`, `Ultra:: Vary Drive Speed: Yes` and `Bad Sector Re-rip:: Drive Speed: 4` (R2025-07-21 log,
  Steve Hoffman forum, 2025-08-23). They also show AR used after frame re-rips: `AccurateRip:
  Accurate (confidence 3) [Pass 1, Ultra 1 to 1, Re-Rip 8 Frames]` (dBpoweramp forum, 2011). The
  "Vary Drive Speed" option has no description in the pages I read.
- **CTDB and repair.** dBpoweramp has no CTDB verification or repair that I could find. On
  2025-06-01 a forum reply to a request for CTDB support said: *"We plan on adding CTDB shortly
  though."* [forum]. Shipped support is not established as of 2026-11-04. Forum users point to
  CUETools for repair.
- **On our track 5.** dBpoweramp would keep `C96464AB` only if some pass returned it, which on our
  counts is rare. Otherwise it would end where we do: every pass agrees, the track is "Secure",
  and AR says "Inaccurate". It has two things we lack:
  1. AR as a stop after every pass, so a single verified pass wins;
  2. speed changes between passes.

## 4. Other rippers: which read is kept

| Ripper | Keeps the data when | Uses AR or CTDB to stop or pick | Changes speed on mismatch |
|---|---|---|---|
| EAC (secure, no C2) | 2 reads agree, or 8 of 16 re-reads agree | No: AR after extraction | On read errors, per a third-party guide |
| dBpoweramp | a pass verifies with AR, or passes agree | Yes: AR stops after any pass | Yes: pass 2 limit, "Vary Drive Speed", re-rip speed |
| CUERipper | a bit-level vote over passes is clear | No: CTDB verify and submit after the rip | No: code present but commented out |
| XLD | 1st and verify read agree, or a "statistically consistent" retry | No: AR can skip the test pass, and a mismatch is logged | Not established |
| whipper | 2 whole-track cdparanoia runs give the same CRC | No: AR checked after the whole disc | No |
| morituri | same as whipper | No | No |
| cdparanoia | overlapping reads agree | No | No |
| upstream cyanrip | `-Z N`: current CRC equals N earlier reads | No: AR printed after the rip | No: `-S` is set once |
| riprip | per-sample counts reach a threshold, or AR or CTDB confirm | Yes: stops a track at confidence ≥ 3 by default | No |

Details, with sources:

- **CUERipper [src].**
  - Each block of 2,400 sectors is read for up to `16 << quality` passes. Reading stops once
    `pass >= quality` and no sector has an unclear vote
    (`CUETools.Ripper.SCSI/SCSIDrive.cs:1151-1189`).
  - `CorrectSectors` takes, for each bit, the value most passes returned, weighted by C2. A sector
    is an error only when the vote margin is small (`SCSIDrive.cs:1070-1112`). A sector that reads
    the same wrong way every pass gets a clear vote and is kept.
  - A per-pass speed table exists, but the sleep that would enforce it and every `SetCdSpeed`
    call are commented out (`SCSIDrive.cs:1145`, `1160-1163`, `248-260`).
  - Modes are "Burst", "Secure" and "Paranoid" (`CUERipper/frmCUERipper.cs:1246`).
  - After the rip it submits to CTDB. It suggests repair only when the ripper itself found failed
    sectors and some CTDB entry `canRecover` (`frmCUERipper.cs:544-556`). In our case the ripper
    finds none, so it would not suggest repair.
- **XLD [doc]** (tmkk.undo.jp version history):
  - *2010-11-20*: the "XLD Secure Ripper" uses *"statistical error correction and a cache
    defeat"*. *"The program performs a retry read when the 1st and the 2nd (verify) read results
    do not match (or when C2 error is detected)."*
  - *2010-10-27*: added *"option to avoid testing when the track exists in AccurrateRip DB"* and
    *"option to treat AccurateRip mismatch as an inconsistency in log"*.
  - XLD's author publishes its source under the GPL ([wiki] *XLD*); I did not read it. CTDB
    doesn't appear in the version history, so **XLD CTDB support is not established**. Speed
    control on mismatch is also **not established**.
- **whipper [src].**
  - `ReadVerifyTrackTask` runs `cd-paranoia` twice into one temp file and computes a CRC32 after
    each run (`whipper/program/cdparanoia.py:477-485`). A mismatch raises `ChecksumException`
    (`cdparanoia.py:531-541`).
  - The whole track is retried up to `DEFAULT_MAX_RETRIES = 5` times (`whipper/command/cd.py:39`,
    `458-489`).
  - AR is fetched and compared only in `verifyImage`, after every track is ripped
    (`whipper/common/program.py:632-666`, called at `cd.py:586`).
  - The `cd-paranoia` command line sets no speed (`cdparanoia.py:274-283`).
- **morituri [src]** is the same design, with `MAX_TRIES = 5` (`morituri/rip/cd.py:41`, `365-389`)
  and a CRC comparison at `morituri/program/cdparanoia.py:507-512`.
- **cdparanoia [doc] [src].**
  - The FAQ says: *"Because the verification algorithm is partially based on rereading and
    comparing vectors, if two vectors read incorrectly but identically, cdparanoia may never
    detect the problem."* On `!`: *"the drive is making continuous silent errors that look
    identical on each re-read, a condition that can't always be detected."*
  - `FIXUP_ATOM`, the event our track 3 counts, is a *rift*, not jitter. The source says
    *"FIXUP_EDGE is actually logging a jitter event, not a rift-- a rift is FIXUP_ATOM --Monty"*
    (`libcdio-paranoia@384f4da:lib/paranoia/paranoia.c:541-552`). `cd-paranoia` draws it as `+`
    (`src/cd-paranoia.c:410-415`). The FAQ explains `+`: *"the drive lost its place while reading
    data, and restarted in some random incorrect location without alerting the kernel. This case
    is also corrected by Paranoia."*
- **Upstream cyanrip [src].**
  - `-Z` is described as "Rip tracks until checksums match N times (for damaged CDs)"
    (`src/cyanrip_main.c:1533`).
  - The loop counts how many earlier reads have the current EAC CRC and stops when that count
    reaches N (`cyanrip_main.c:1163-1197`). So `-Z 1` ends on 2 agreeing reads, and `-Z 2` ends
    on 3 agreeing reads. The brief describes the fork's `-Z 2` as stopping at 2 agreeing reads.
    **I did not read the fork**, so I don't know whether it changed this.
  - Only the read that ends the loop is encoded (`repeat_mode_encode`).
  - AR is fetched before ripping (`cyanrip_main.c:2029`) and printed after, never consulted in the
    loop.
  - `-S` sets the speed once (`cyanrip_main.c:242-251`).
- **riprip [src] [doc].**
  - It keeps up to 3 candidate values per sample, with counts (`riprip_core/src/rip/sample.rs`,
    `ContentiousSample`).
  - A sample is "likely" when its value was read at least `ABS` times and `MUL` times more often
    than any rival (`sample.rs:115-124`; default `2,2`, man page `release/man/riprip.1:67`).
  - After each pass it checks the track's best values against AR and CTDB. A track at
    `--confidence` (default 3) or above is confirmed and skipped from then on
    (`riprip_core/src/rip/mod.rs:723-742`, `956-972`; man page line 55).
  - It also offers backwards and alternating read order (`--backwards`, `--flip-flop`) and cache
    busting.
  - It doesn't repair. Its README says: *"If Rip Rip can't confirm the rips, toss them into
    CUETools to see if they're close enough for automatic repair."*
  - On our track 5 it would keep the majority wrong value. Only a pass whose best values matched
    AR or CTDB would end the track.

## 5. CTDB verification and repair

### Data and endpoints [src]

- **Lookup** (`CUETools.CTDB/CUEToolsDB.cs:70-82`):

  ```text
  GET http://db.cuetools.net/lookup2.php?version=3&ctdb=1&fuzzy=0|1&metadata=...&toc=...
  ```

  The TOC is the colon-separated start sectors and the lead-out, with `-` before data tracks
  (`CUETools.CDImage/CDImage.cs:511-517`).
- **Response.** XML `<entry>` elements with `id`, `crc32` (whole-disc CRC, the CTDBID),
  `confidence`, `npar`, `stride`, `hasparity` (a URL), `syndrome` or `parity` (base64),
  `trackcrcs` and `toc` (`CUETools.CTDB.Types/CTDBResponseEntry.cs:9-28`).
- **Live example (2026-11-04).** A lookup of the synthetic TOC `0:15000:30000:45000` returned:

  ```xml
  <entry confidence="1" crc32="146b974e" hasparity="http://p.cuetools.net/10623994"
    id="10623994" npar="8" stride="5880" syndrome="hThGM1q1VerhtkLbsd45HQ=="
    toc="0:15000:30000:45000" trackcrcs="71dea5ed 713dac27 b34c611d" />
  ```

  A `HEAD` request on the `hasparity` URL returned `content-length: 188160` from Amazon S3, which
  is 8 × 11,760 × 2 bytes. This is a network check of the service's format. It says nothing about
  our program.
- **Parity fetch.** CUETools requests HTTP byte ranges of the `hasparity` file, first for
  `npar` = 4 (94,080 bytes), then 8 (188,160 bytes in total), then 16 (376,320 bytes)
  (`CUEToolsDB.cs:200-262`, `457-470`). It checks the first column of the download against the
  syndrome in the lookup and rejects a mismatch as `Conflict` (`CUEToolsDB.cs:255-259`). Byte
  ranges were not tested here.
- **Submit.** `POST /submit2.php` (`CUEToolsDB.cs:346-389`). Only CUETools, CUERipper and the EAC
  CTDB plugin submit ([doc] cue.tools wiki, *CUETools Database*).

### The algorithm [src] [forum]

- **The code.** Reed-Solomon over GF(2¹⁶), generator polynomial `0x1100B`
  (`CUETools.Parity/Galois.cs:550-556`). The decoder is based on Masayuki Miyazaki's
  `reedsolomon` project (`CUETools.Parity/RsDecode.cs:10-11`).
- **The layout.** The disc's audio after the first-track pregap is read as 16-bit words and laid
  out in rows of 11,760 words: 5,880 stereo samples, or 10 sectors. Each column is one codeword
  (`CDRepair.cs:22-33`; `CUEToolsDB.cs:509` sets `10 * 588 * 2`). The first row (10 sectors) and
  the last 10 to 20 sectors are outside the code.
- **Chudov's own description** [forum, Hydrogenaudio topic 79882, 2010]: *"16-bit Reed-Solomon can
  be used directly only on chunks of up to 64k words ... So i have to process the file as a
  matrix with rows of 10 sectors (5880 samples == 11760 words/columns) ... N-word recovery record
  can detect and correct up to N/2 erroneous words, so this 8-word recovery record can detect up
  to 4 errors in each column."*
- **Offset.** `FindOffset` tries every offset within ±5,879 samples, comparing the local
  single-row syndrome with the one in the lookup (`CDRepair.cs:103-157`). CTDB doesn't need the
  drive offset.
- **Repair.** `VerifyParity` XORs the local and database syndromes for each column and runs
  Berlekamp-Massey, Chien search and Forney. It gives up if any column has more than `npar/2`
  errors (`CDRepair.cs:159-226`). It then applies the corrections to the whole-disc CRC and
  accepts the repair only if the result equals the entry's `crc32` (`CDRepair.cs:220-233`). A
  wrong decode would have to collide with that 32-bit CRC to pass.
- **After repair.** CUETools runs AR on the repaired output. Its comment reads: *"we use AR after
  CTDB fix, so that we can verify what we fixed"* (`CUETools.Processor/CUESheet.cs:3663-3666`).
  The `repair` script makes the user pick an entry (`CUESheet.cs:4489-4523`).
- **Units.** CTDB's "samples" are 16-bit words, one channel each. `Differs in 3 samples` means 3
  channel values, which could sit in 1 to 3 stereo samples. The positions are in word units
  (`CDRepair.cs:212-223`). The per-track `@mm:ss:ff` is relative to the track start
  (`CUEToolsDB.cs:647-662`).

### How much it can fix

- **[src] Per column:** `npar/2` words (`CDRepair.cs:178`, `202`).
- **Contiguous damage:** the most is `npar/2` × 10 sectors: 20, 40 or 80 sectors for `npar` 4, 8
  or 16.
- **[doc] The CTDB wiki:** *"The best case scenario is when there's one continuous damaged area
  up to 30-40 sectors (about half a second) long for most discs. As of CTDB 2.0, one continuous
  damaged area up to about 75 sectors (a second) on popular discs. The worst case scenario is 4
  non-continuous damaged sectors in (very) unlucky positions."*
- **[doc] CUETools changelog** (2.1.4, 2012-04-16): *"CTDB 2.0: popular CDs can have twice larger
  correction files"*.

### Confidence

- **[doc]** *"CTDB 2.0: confidence values no longer include AccurateRip data"* (changelog
  2.1.4).
- **[src]** The total in `(x/Total)` is the sum of every entry's confidence for the TOC
  (`CUEToolsDB.cs:113-120`). A track's `x` adds up the entries the track matches, including
  entries that differ from the rip only in other tracks (`CUEToolsDB.cs:549-591`).
- **[doc] Use.** The cue.tools wiki rule of thumb: *"a CTDB confidence of 2/X or higher indicates
  that the rip in the database is probably undamaged."* The *CTDB EAC Plugin* page warns that
  older EAC versions reported quality as 100% when it wasn't, which *"causes CTDB to wrongly
  accept a recovery record which could be used to 'repair' future rips to match the bad rip ...
  It is recommended to avoid doing a repair when the CTDB confidence is 1/x."*
- **[forum]** korth, Hydrogenaudio topic 123749, 2023: *"The same user cannot confirm and/or add
  to a CTDB ID more than once."*

### Licensing

The sources disagree:

- The repository's `License.txt` says CUETools is GPL version 2 or later.
- The cue.tools wiki says *"The sample client library is open source, LGPL"* and *"The database
  contents is public domain"*. Chudov wrote in 2010 that *"the code required to use it is LGPLed
  as all CUETools libraries"* [forum].
- `CUETools.AccurateRip`, `CUETools.CTDB` and `CUETools.Parity` carry no per-file headers.
  `CUETools.CLParity` says LGPL 2.1 or later.
- The license of Miyazaki's original Reed-Solomon code is **not established**.

**Safe reading:** treat a port as GPL-2.0-or-later unless Chudov confirms LGPL in writing.

### Implementations outside C#

- **Repair, corrected 2026-11-04:** `neheb/cdverify` (Rust, GPL-3.0, created 2026-10-11) says
  in its README that it can "repair them with CTDB parity data". This report missed it, and
  Platterpus's research found it. Its code was not read here.
- **Repair, as first written: none found.** In 2018 Chudov wrote in whipper issue 15: *"As far as i know, yes [the
  C# client is the only one]. The network protocol part is quite trivial, but the parity
  calculations ... a bit more work."*
- **Per-track CRC verification, no parity:**
  - Rust: `cdtoc`, used by riprip, WTFPL.
  - Python: `python-cuetoolsdb`, a partial port from 2022, GPL-2.0, with useful notes in
    `api.org`.
  - Python: `py-cuetools`, TOC lookups only.
- **Repair from Linux:** `ctdb-cli` is C# on .NET 10 and links the CUETools libraries (GPL-3.0).
  It offers `verify` and `repair test.cue [--target <CRC>]`. `LynxTWO/cuetools-linux` is a .NET
  application whose README calls it "built, unreleased".

### Could our 3-sample error be repaired from the majority entry's parity?

Yes, in principle, and with a wide margin:

- Three adjacent or nearby words fall in different columns, which is at most 1 error per column.
  Even the first 94 KB fetch (`npar` 4, 2 per column) covers that.
- Position 02:24:59 of track 5 is far from the excluded first and last rows.

The conditions:

1. **The whole disc.** All 14 tracks, contiguous. CTDB parity covers the disc, not a track.
2. **The rest of the disc within limits.** The rip's other tracks must match the 1,423 entry, or
   differ from it within the per-column limit. A wrong track 3 read in the same image adds its
   own errors.
3. **The final CRC check.** The repaired image must hash to the entry's `crc32`, which
   `VerifyParity` enforces.

Two independent cross-checks follow a repair. First, AR on the repaired track 5 should verify.
Second, its EAC CRC32 should equal `C96464AB`, the value this drive returned on 2026-10-06. That
gives three unrelated sources: CTDB submitters, AR submitters (EAC and dBpoweramp), and our own
drive.

## 6. Public discussion of this pattern

All of the following are forum reports, not documentation.

- **Steve Hoffman Music Forums, "EAC - differs in x samples?", 2022-05-24/26.**
  - One poster quotes his EAC secure log: "No errors occurred", AR `cannot be verified as
    accurate` on one track, CTDB `Differs in 2 samples @07:11:52,07:28:69`. *"So I switched to a
    different ripping drive and tried again. This time I got a good rip."*
  - Another advises cleaning the disc, then another drive: *"The different drive will often rip
    without errors."*
  - A third lists four options: ignore it if inaudible, run CUETools repair, re-rip with Test &
    Copy, or try another drive.
- **Hydrogenaudio topic 94318, 2012.**
  - The user's EAC rip had matching Test and Copy CRCs, AR "cannot be verified", and CTDB
    `(2/2) Differs in 9 samples`. He re-ripped with another drive and got the same CRCs.
  - Chudov replied: *"My guess is that the CD masters slightly differ ... It's hard to determine
    in such cases which one is correct. So my advice - don't repair it."*
  - Another reply named drive caching as a possible cause of agreeing reads and suggested
    re-ripping with "the drive does cache" and C2 off.
  - **The discriminator:** the same CRC from two drives points to the disc. Our case differs:
    our own drive once returned the AR-verified value.
- **Hydrogenaudio topic 110379.** A reply notes a rival explanation: a rare pressing that differs
  by a few samples, which would show up only when *"someone else with the same pressing gets the
  same result"*. It suggests a second drive to settle it.
- **Hydrogenaudio topic 123749, 2023.** korth explains that CTDB's "or" lines mean the rip can be
  repaired to match that entry. Another user reports repairing three damaged tracks with
  CUETools.

**What experienced users recommend, in order:** clean the disc and re-rip; try another drive;
use CUETools repair when the CTDB entry has confidence of 2 or more and the rip's own drive can't
produce the majority value; don't repair when two drives agree with each other against the
database.

## Options for us

Under `docs/OWNERSHIP.md`, the ripper owns anything that needs the disc and the app owns anything
derived afterwards. Every ripper option below changes drive I/O or the log. Each needs hardware
verification on the BDR-209D, and log changes are handshake material. Track outcomes marked
*expected* follow from the facts in the brief and haven't been run.

### Ripper (needs the disc)

**R1. Test every whole-track read against AR and keep a verified read even when it is outvoted**
(dBpoweramp's stop rule, riprip's `--confidence`).

- **Track 5:** on 2026-10-06 it would have kept `C96464AB` instead of keeping `E0036697` by
  agreement. On other days it changes nothing unless a verified read turns up within the read
  budget.
- **Track 3:** it keeps `59D352DD` the first time it appears, which can only shorten the run. If
  two wrong reads, such as a recurring `3D8FCF0C`, agree before that, the agreement rule still
  ends the track. Closing that gap means not accepting agreement alone while AR has the disc and
  the read budget isn't spent.
- **Cost:** low. AR is already fetched before ripping (upstream `cyanrip_main.c:2029`) and the
  checksums are already computed per read, so this adds a comparison in the `-Z` loop and a log
  line naming the rule that chose the read.
- **Limits:**
  - It needs the disc and track in AR.
  - Match on v2, or on v1 only where no v2 entry exists, because v1 drops part of the right
    channel.
  - Each AR entry adds about a 2⁻³² chance of a false match.
  - It changes what "kept" means, from "read consistently" to "verified by AR", and the log must
    say which.

**R2. Log every distinct read** with its checksum, count, AR result, and paranoia `FIXUP_ATOM`
(rift) count. Optionally keep each alternate's audio.

- **Track 5:** the 2026-10-06 log would show `C96464AB` × 1 with an AR match next to
  `E0036697` × 2 with none, so the app could see that a verified read existed. With the audio
  kept, the app could select it after the fact.
- **Track 3:** it would show whether rift counts separate right reads from wrong ones on more than
  the runs seen so far.
- **Cost:** log lines, a handshake round, and about 50 MB of WAV per kept alternate.
- **Limits:** it records the problem and fixes nothing by itself.

**R3. Keep per-sector CRCs for every read and re-read only the disputed sectors**, with cache
defeat. Accept a splice only if the track's AR v2 checksum then matches. AR is a linear sum, so
changing one sector's data updates the checksum in 588 steps.

- **Track 5:** this needs one read that differs, like 2026-10-06's, to find the sectors. The
  targeted re-reads are then a few sectors each, so dozens of tries take seconds to minutes
  rather than dozens of whole-track passes.
- **Track 3:** comparing a `59D352DD` read with a `3D8FCF0C` read finds the unstable sectors.
  Voting on those, followed by an AR check, should converge even when whole-track CRCs rarely
  agree.
- **Cost:** moderate C work: per-sector CRC arrays, kept data for the disputed sectors, and AR
  delta arithmetic.
- **Limits:**
  - It can't help if every read of a sector is identical.
  - Trying `2^k` combinations multiplies the false-match chance by `2^k`, so cap `k` and log the
    number of candidates.
  - No established ripper documents this splice. dBpoweramp's "cross-check ... elements in each
    of the pass" may be similar, but that is not established.

**R4. Change read conditions when reads disagree or AR fails:** speed through
`cdio_cddap_speed_set`, read order (riprip's backwards and flip-flop), paranoia mode, and cache
busting distance.

- **Tracks 5 and 3:** unknown until run. The rift correlation on track 3 suggests read conditions
  matter on this drive. dBpoweramp's documents say some drives *"reading at a different speed ...
  detect more errors"*.
- **Cost:** drive time.
- **Limits:** drives may ignore speed requests (upstream `cyanrip_main.c:242`). The effect is
  specific to this drive, so it needs a rig session for each setting.

**R5. A second drive.** Users recommend it most often. It is the owner's hardware decision and
outside this repository.

### App (after the rip)

**A1. CTDB repair from parity** (CUETools' algorithm).

- **Track 5:** expected to repair the 3 words with the first 94 KB of parity. CTDB's own CRC
  check confirms the result. AR on the repaired track, and its CRC32 against `C96464AB`, give two
  more checks.
- **Track 3:** it repairs the image if the kept track 3 read differs from the majority within the
  per-column limit. The size of the difference is unknown.
- **Cost:** either a Python GF(2¹⁶) Reed-Solomon implementation, or a separate program such as
  `ctdb-cli` (.NET 10, GPL-3.0) or CUETools under Wine. A Python version needs syndromes over
  about 30,000 rows × 11,760 columns; vectorized NumPy should manage that, though this isn't
  measured. Network use is one lookup plus 94 to 376 KB of parity per non-matching entry.
- **Limits:**
  - Whole disc only. No HTOA, and nothing in the first 10 sectors of track 1 or the last 10 to 20
    of the last track.
  - At most `npar/2` words per column.
  - Don't repair from a confidence-1 entry, as the *CTDB EAC Plugin* page advises [doc].
  - The licensing is unclear (see *Licensing*).
  - Repaired words weren't read from the disc. The record must keep the original rip and state
    each changed word's position and the entry ID used. This is derived data, so it belongs to
    the app under `OWNERSHIP.md`.

**A2. Choose among alternates the ripper kept** (needs R2 with audio kept).

- **Track 5:** it would have chosen `C96464AB` on 2026-10-06.
- **Track 3:** it picks `59D352DD` whenever a run produced it.
- **Cost:** a selection rule and a provenance line.
- **Limits:** it is only as good as the alternates the ripper kept.

**A3. Check whether the drive interpolated.** After a repair, compare our 3 wrong words with
their neighbors. Values that equal a straight-line interpolation would suggest the drive concealed
an error it didn't report.

- **Track 5:** a diagnosis, not a fix.
- **Cost:** low.
- **Limits:** not established as a reliable test. dBpoweramp says it detects interpolation but
  doesn't publish how.

**A4. Keep the current CTDB per-track verification and AR reporting** as the detector. Existing
Rust and Python code shows it is cheap. It already found this case.

### What only a run can settle

- Whether EAC, dBpoweramp or riprip on the BDR-209D return `E0036697` for track 5.
- Whether a lower speed, the reverse read order, or paranoia off changes track 5's or track 3's
  result on this drive.
- How often this drive returns `C96464AB`. That rate decides whether R1 alone is worth having.
- Whether CTDB repair of the full current rip succeeds. This needs the whole-disc image, not
  track 5 alone.

## Sources

Read 2026-11-04 unless marked otherwise.

- Spoon, "AccurateRip CRC Calculation", dBpoweramp forum, 2010-02-16 (v2 addendum 2010-03-29):
  <https://forum.dbpoweramp.com/forum/other-topics/developers-corner/20117-accuraterip-crc-calculation>
- Hydrogenaudio Knowledgebase, *AccurateRip*:
  <https://wiki.hydrogenaudio.org/index.php?title=AccurateRip>
- Exact Audio Copy, *Extraction technology*, *FAQ*, *AccurateRip*:
  <https://www.exactaudiocopy.de/extraction-technology/>, <https://www.exactaudiocopy.de/faq/>,
  <https://www.exactaudiocopy.de/accurate-rip/>
- Hydrogenaudio Knowledgebase, *EAC Drive Options*, *EAC Options*:
  <https://wiki.hydrogenaudio.org/index.php?title=EAC_Drive_Options>,
  <https://wiki.hydrogenaudio.org/index.php?title=EAC_Options>
- roozster.info, *EAC* (third-party guide): <http://roozster.info/eac/05.html>
- *Spoon's Audio Guide: CD Ripping*: <https://www.dbpoweramp.com/spoons-audio-guide-cd-ripping>
- dBpoweramp help, *CD Ripper: Advanced Options*: <https://dbpoweramp.com/Help/dMC/CDadvanced>
- dBpoweramp, *CD Ripper Setup Guide*: <https://doc.dbpoweramp.com/dmc/en/cd-ripper-setup-guide.htm>
- Illustrate, *Secure ripper* test (vendor, undated): <http://www.cd-ripper.com/secure-ripper.htm>
- dBpoweramp forum, CTDB request with reply, 2025-06-01:
  <https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/332418-suggestion-for-cd-ripper-add-ctdb-and-other-verification>
- dBpoweramp forum, BDR-XD05 pass behavior, 2017-02-26:
  <https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/35356-why-does-secure-rip-some-tracks-twice-on-one-occasion-but-once-on-others>
- dBpoweramp forum, re-rip log, 2011-06-15:
  <https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/23602-learning-more-about-log-info>
- Steve Hoffman forum, dBpoweramp R2025-07-21 log, 2025-08-23:
  <https://forums.stevehoffman.tv/threads/dbpoweramp-vs-accuraterip-vs-cuetools.1231894/>
- XLD version history: <https://tmkk.undo.jp/xld/index_e.html>
- cdparanoia FAQ: <https://www.xiph.org/paranoia/faq.html>
- cue.tools wiki, *CUETools Database*, *CTDB EAC Plugin*, *CUETools Changelog*:
  <https://cue.tools/wiki/CTDB>, <http://cue.tools/wiki/CTDB_EAC_Plugin>,
  <https://cue.tools/wiki/CUETools_Changelog>
- Hydrogenaudio topic 79882, "CUETools DB" (2010):
  <https://hydrogenaudio.org/index.php/topic,79882.0.html>
- Hydrogenaudio topic 94318 (2012): <https://hydrogenaudio.org/index.php/topic,94318.msg791382.html>
- Hydrogenaudio topic 110379: <https://hydrogenaudio.org/index.php/topic,110379.0.html>
- Hydrogenaudio topic 123749 (2023): <https://hydrogenaudio.org/index.php/topic,123749.0.html>
- Steve Hoffman forum, "EAC - differs in x samples?" (2022):
  <https://forums.stevehoffman.tv/threads/eac-differs-in-x-samples.1146451/>
- whipper issue 15, "CTDB as an alternative to AccurateRip":
  <https://github.com/whipper-team/whipper/issues/15>
- fre:ac issue 389, CTDB verification write-up: <https://github.com/enzo1982/freac/issues/389>
- Repositories in the table at the top, read from shallow clones.
