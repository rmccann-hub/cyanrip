# Drive-side settings that affect CD-DA read accuracy, and what Linux can read or set

Researched 2026-11-04 (UTC). Every web source was retrieved that day; every
source tree was a shallow clone made that day, cited as `repo@commit:path:line`.
Labels: **[spec]** a T10 draft; **[vendor doc]** a drive maker's own page,
manual or command reference; **[src]** source code; **[db]** a drive database;
**[wiki]** a community wiki; **[forum]** forum posts, reviews and blogs (third
parties, including review sites quoting a vendor). "Not established" means no
source was found, not that the thing is false.

## Answer

The setting most likely to decide what the rig's BDR-209D does at the bad spot
is Pioneer's PureRead. In Pioneer's own words, Standard (PureRead off)
interpolates over an error CIRC cannot correct; Master retries with changed read
parameters and **still interpolates, silently, if the retries fail**; Perfect
retries and then stops reading instead of interpolating [vendor doc]. Pioneer
itself warns that many real errors are reproducible, so re-reading interpolates
the same way every time and a comparison of reads cannot catch it [vendor doc,
dev story vol. 17 and 27]. That fits the rig's symptom, but it does not prove it.
**One library reads PureRead, through a Pioneer vendor command.**
`pioneer-optical` (Rust, MIT) reads Pioneer's 256-byte settings block with
READ BUFFER `3Ch`, mode `02h`, buffer `F4h`: byte 9 says whether PureRead is
supported, and bytes 4 and 5 give the mode [src
pioneer-optical@d2cbbf2:src/settings/f4.rs:52-80,92-94]. Platterpus found it,
and this report's first draft missed it (§1, *Can it be read or set over
SCSI?*). No standard MMC command reads PureRead. QPxTool defines the three mode
values but its `pioneer_set_pureread()` is an empty stub; cdrtools, libcdio,
libcdio-paranoia, redumper, DiscImageCreator, whipper and CUETools contain
nothing for it [src]. **Whether the BDR-209D has
PureRead at all is not established:** Pioneer documents the retail BDR-209
models as "PureRead2" (no "+", and "+" is Pioneer's name for settings stored in
the drive), the BDR-209DBK product specification lists no PureRead, Pioneer's
Drive Utility download lists the 209EBK/209UBK but not the 209DBK, and one forum
answer says bulk models lack it [vendor doc, forum]. `pioneer-optical`'s
census of Pioneer firmware images finds the settings handler of two firmware
1.51 images storing a literal 0 at byte 9, PureRead's support byte, which its
own scope note calls "not runtime support proof" [src
pioneer-optical@d2cbbf2:tests/evidence/device-settings-hoard-2026-10-08.json:4535,5064].
Platterpus reports those images match the owner's BDR-209D 1.51 download by
SHA-256; this report has not checked that. The drive's own answer to the read
above settles it. Of the standard MMC
controls, Pioneer's BDR-203 command reference says the drive **ignores** the
error recovery page's AWRE, ARRE, TB, RC, DTE, DCR and retry count, says the
caching page "has no effect", and says no command can set the read speed
[vendor doc]. The one standard control written for this case is READ CD's DAP
bit: with DAP 0 the drive "should not" mute or interpolate CD-DA (MMC-5/6), and
libcdio already sends DAP 0 [spec, src]. A Linux program can therefore *read*
what the drive declares (mode pages 01h, 08h and 2Ah; GET CONFIGURATION features
001Eh and 0107h) and *observe* behaviour (sense data, timing, data). It can
read PureRead's support and mode only through Pioneer's vendor READ BUFFER
above. A C1/C2/CU scan on Linux needs a drive QPxTool supports with full
CIRC counters (Plextor PX-7xx/Premium, BenQ DW16xx, MediaTek-era LiteOn), at
one-second resolution. QPxTool's Pioneer plugin always reports CU as 0.

## Corrections to the brief

- **This report's first draft said no command reads PureRead.** It missed
  `pioneer-optical`, a Rust library created in 2026 that reads Pioneer's
  settings block, PureRead's support and mode among it, which Platterpus found
  the same day (platterpus@8287eb9c). Dumbass us: the search covered QPxTool,
  cdrtools and six rippers, and not the newest library written for exactly
  these drives. The answer, §1 and the table are corrected.

These come from the sources, and each needs the same scrutiny as any other claim.

- **redumper's BDR-209D row is for firmware 1.10, not 1.51.** The row is
  `{ "PIONEER", "BD-RW BDR-209D", "1.10", ..., +667, 0, 0, BE, DATA_SUB, GENERIC }`
  under `// GENERIC (BAD) DRIVES BELOW THIS LINE`, with the comment
  "BE_CDDA unscrambles data sectors" [src redumper@fa5d243:drive.ixx:217,239].
  redumper matches on vendor, product *and* revision. For any other revision it
  logs "warning: unsupported drive firmware" and uses its generic configuration
  [src redumper@fa5d243:drive.ixx:336-345]. So "listed as bad with no C2" is
  true of 1.10. For 1.51 it is an inference.
- **Master is not "retry instead of interpolate".** Pioneer's manual: "if it
  encounters audio data that cannot be completely reproduced, it interpolates
  that data and continues" [vendor doc, BDR-S13UBK manual]. Only Perfect refuses
  to interpolate.
- **The default differs by generation.** On the BDR-2207 (BDR-207M) the Drive
  Utility's Standard mode "is the default setting" [forum, cdrinfo review quoting
  the utility]. On the BDR-S13UBK (PureRead4+) Master "(default setting)" and
  PureRead "is turned on as a default setting" [vendor doc]. The BDR-209D's
  default is not established.

## 1. PureRead

### Modes and what each does to error handling

| Mode | Pioneer's description | Source |
|---|---|---|
| Standard / OFF | "normal acquisition of music CD data. If there is a scratch that prevents reading, interpolation will occur." | [vendor doc] BDR-S13UBK manual, "Useful Functions" |
| Master | "works to acquire and reproduce the original sound as much as possible, but if it encounters audio data that cannot be completely reproduced, it interpolates that data and continues with acquisition." | [vendor doc] same |
| Perfect | "if it encounters audio data that cannot be completely reproduced, it stops and halts acquisition." | [vendor doc] same |
| Perfect (Japanese) | 「パーフェクトモードでは、データ補間がどうしても必要な場合はディスクからの読み出しを中止いたします」: in Perfect mode, when interpolation is unavoidable, reading from the disc is aborted. A successful Perfect-mode rip is "guaranteed" original sound. | [vendor doc] dev story vol. 27 |
| Real Time PureRead (3 and later) | Works during real-time playback: retries, and interpolates when the playback deadline is missed. | [vendor doc] BDR-S09J-X press release; [forum] Spoon |

Third-party restatements agree and add detail. **No source gives the sense key
or ASC that Perfect mode returns.**

- Spoon (dBpoweramp's developer), citing Pioneer vol. 17 and 27: Standard "when
  C2 error happens, interpolate sample gap and read continues"; Master "change
  read parameter and retry … if several retry failed, interpolate"; Perfect
  "when several retry failed, reports read error to OS and stop ripping"
  [forum, 2024-07-04].
- cdrinfo's BDR-2207 review quotes the utility: errors "cannot be corrected by
  CIRC" trigger the mode. In Perfect "a read error is returned and the drive
  operation will STOP" [forum].
- A 2007 post about the DVR-115D says re-reads go "up to a maximum of 40 times"
  [forum, unverified].

The mechanism, in Pioneer's account [vendor doc, vol. 17]:

- PureRead retries with parameters changed for fingerprints, scratches, dust
  and warp.
- Too many retries make the OS raise an error, so retries are tuned to the OS.
- 「実際のエラーの中には、再現性が良いものも多く、何度繰り返して読んでも同じようにデータ補間をして読み出してしまい、補間に気付かないケースが発生する」:
  many real errors are reproducible, so however often you re-read, the drive
  interpolates the same way and the interpolation goes unnoticed.

Vol. 27 adds:

- Comparing several rips cannot detect interpolation that the drive inserts at
  the same place every time.
- A PureRead4 correction pass takes several milliseconds (29 ms measured
  maximum) and repeats. Correcting a hard spot can take tens of seconds, while
  the PC expects data within seconds.

Pioneer's product pages add that PureRead does nothing on discs that need no
interpolation, and does not work properly on non-standard discs such as CCCD
[vendor doc, BDR-S09J-BK and BDR-211JBK pages].

### Generations

| Name | What changed (Pioneer) | Examples documented by Pioneer |
|---|---|---|
| PureRead | Retry with changed parameters | DVR-115D (2007) [forum] |
| PureRead2 | Improved algorithm and circuit | **BDR-209JBK (Jan 2014)** [vendor doc]; BDR-209MBK and BDR-2209 ("PureRead2") [vendor doc] |
| "+" suffix (PureRead+, 2+, 3+, 4+) | 「設定値をドライブに記憶、保持できる＋機能」: the "+" adds storing and holding the settings in the drive | vol. 17 and 27 [vendor doc]; BDR-XD05J "PureRead2 +" [forum, cdrinfo 2014] |
| PureRead3 / 3+ | Works during real-time playback | BDR-S09J-X, BDR-S09J-BK, BDR-211JBK, BDR-212JBK [vendor doc] |
| PureRead4+ | Several read settings used at once (before 4, one per read); processing unit over 100× finer | BDR-S11J-X/BK, BDR-S13UBK [vendor doc] |

For the **BDR-209D** (bulk/OEM "DBK"):

- Pioneer's BDR-209DBK Product Specification Rev 1.01 (2014-01-23) has a
  features list with no PureRead [vendor doc].
- Pioneer USA's BDR-209DBK page names no PureRead in its highlights
  [vendor doc].
- Pioneer's Drive Utility table lists "BDR-209EBK BDR-209UBK(BDR-2209)" with
  `PioneerBDR-209-211_DriveUtility_v1.2.0.3.exe` and no 209DBK row
  [vendor doc, pioneer.jp dev00001r_e].
- Asked whether the BDR-209XJBK/WS2 bulk drive has PureRead, a kakaku.com user
  answered 「バルク品は非対応です」 ("bulk products are not supported"), adding
  that the difference is firmware [forum, 2016-09-25, unverified].

**Status: not established that the BDR-209D firmware 1.51 implements PureRead,
or that the Drive Utility will recognise it.**

### Persistence across power cycles, hosts and OSes

- With "+": "Select [Save settings to drive]. The set values will be saved to
  the drive. Settings will be retained even after turning off the device power."
  Without that box, "the settings will revert to the previously saved settings"
  at power-off [vendor doc, BDR-S13UBK manual]. The state lives in the drive, so
  it follows the drive to any host or OS.
- Without "+": Spoon paraphrases Pioneer: "Drive forget Pure Read settings on
  power cycle: Need to run Drive Utility app every time drive power is plugged"
  [forum]. Pioneer's vol. 17 says the "+" is what adds storing in the drive.
- **The BDR-209 line is "PureRead2" without "+".** If the BDR-209D has PureRead
  at all, a setting made in Windows may not survive the drive losing power.
- Not established: whether a warm reboot, a SATA link reset, or a Linux libata
  error-handling reset (which can follow a command timeout) reverts an unsaved
  setting.
- Side effect on the BDR-S13UBK: with PureRead on, maximum CD audio and CD-ROM
  speed is 40× [vendor doc]. The BDR-209DBK specification lists "CD-DA (Data
  extraction) 24X CAV" and says "The read speed will be slow down automatically
  in case uncorrectable read error happens" [vendor doc].

### Can it be read or set over SCSI?

**Read, yes, by one library; set, by the same library's untested encoding.**
What each source holds:

- **`pioneer-optical`** (Rust, MIT, last commit 2026-11-01), which this
  report's first draft missed and Platterpus found (their
  `docs/eac-parity.md`, platterpus@8287eb9c):
  - It reads Pioneer's settings block with READ BUFFER `3Ch`, mode `02h`,
    buffer `F4h`, 256 bytes: `[0x3c, 2, 0xf4, 0, 0, 0, 0, 1, 0, 0]` [src
    pioneer-optical@d2cbbf2:src/settings/f4.rs:92-94].
  - Byte 9 is PureRead's support flag. Bytes 4 and 5 give the mode: 0 is
    Standard, 1 then 8 Master, 1 then 254 Perfect. Byte 28 is Real Time
    PureRead and byte 29 its support; byte 49 the PureRead generation; bytes
    2 and 3 the current and saved quiet mode [same file:28-80].
  - It sets PureRead with WRITE BUFFER `3Bh`, mode `01h`, buffer `FAh`
    [same file:155-171]. Writing changes the drive; nothing in this project
    should send it.
  - Its census of Pioneer firmware images, by static analysis, finds two
    firmware 1.51 images (`sat/8600/ID61` and `sat/8601/ID61`) whose settings
    handler stores 0 at byte 9 [src
    pioneer-optical@d2cbbf2:tests/evidence/device-settings-hoard-2026-10-08.json:4535,5064].
    Its scope note: "Literal observations are not runtime support proof."
- **QPxTool** has the values `PIO_PURE_READ_STD 0x00`, `PIO_PURE_READ_MASTER 0x01`
  and `PIO_PURE_READ_PERFECT 0x02` [src qpxtool@8cf1003:lib/qpxpioneer/include/pioneer_spdctl.h:27-34].
  It has a `char pureread;` field [src qpxtool@8cf1003:lib/qpxtransport/include/qpx_mmc.h:324].
  But `int pioneer_set_pureread(drive_info* drive, char pr) { return 0; }`
  sends nothing [src qpxtool@8cf1003:lib/qpxpioneer/pioneer_spdctl.cpp:68-71].
  The 2026 fork is the same [src speed47/qpxtool@ae6f7b4:lib/qpxpioneer/pioneer_spdctl.cpp:65].
  Nothing in QPxTool reads it.
- **QPxTool does reach two other Pioneer vendor settings**, which shows how
  Pioneer stores drive settings:
  - QuietMode and speed limit are read by READ BUFFER `3Ch`, mode `01h`,
    buffer ID `F4h`, 256 bytes: byte 0 is the limit, byte 2 the quiet mode
    [src qpxtool@8cf1003:lib/qpxpioneer/pioneer_spdctl.cpp:18-29].
  - They are set by SET CD SPEED `BBh` with vendor values in MMC-reserved
    bytes: byte 1 `0x04` (or `0x0C` to save), bytes 2-3 the limit, byte 10
    `0x80|mode` (or `0xC0|mode` to save) [same file:31-41].
  - `cdvdcontrol --pio-limit` "limit (or not) read speed by 24x for CD and 8x
    for DVD"; `--pio-nosave` "changes will be lost after reboot"
    [src qpxtool@8cf1003:console/cdvdcontrol/cdvdcontrol.cpp:313-315].
  - A MakeMKV user ran `cdvdcontrol --pio-quiet perf` on a BDR-UD04 under
    Linux and read the result back with `-c` [forum]. The vendor buffer still
    answered on a 2010s Pioneer BD drive. QPxTool reads it with mode `01h`;
    `pioneer-optical` reads the same buffer ID with mode `02h`, PureRead
    included.
- **cdrtools** knows only Pioneer DW-S114X and DVD-R S101 writers, and has no
  PureRead [src schilytools@e835e64:cdrecord/scsi_cdr.c:2476-2482; grep found
  nothing].
- **DiscImageCreator** defines legacy Pioneer SCSI-2 opcodes (`D8h` READ CDDA,
  `D9h`, `DAh`, `DBh`, `DFh`, `E0h`, `E3h`, `E4h`), most disabled with `#if 0`.
  It has no PureRead [src DiscImageCreator@9269234:DiscImageCreator/forwardDeclaration.h:160-173].
- **libcdio, libcdio-paranoia, redumper, whipper and CUETools**: no Pioneer
  vendor control and no PureRead (grep, at the commits listed in Sources).
- **Pioneer's own BDR-203/BDC-203 Command Reference** (v1.01, 2009) is the
  nearest public Pioneer BD command document. Its vendor-unique items are
  READ BUFFER and WRITE BUFFER only ("This command is used for checking the
  drive"). Its mode pages are 01h, 05h, 08h, 0Eh, 1Ah, 1Dh and 2Ah, with no
  vendor page, and "The drive is not supported the Parameters Savable (PS) bit"
  [vendor doc, §4.12.2, §4.15, §4.23]. The BDR-203 predates PureRead on BD
  drives, so this does not settle where the BDR-209 keeps it.

## 2. Standard MMC/SPC settings any drive may honour

On Linux all of these go through SG_IO: libcdio's `mmc_run_cmd()` and
`mmc_mode_sense_10()`, or sg3_utils (`sg_modes`, `sg_wr_mode`, `sg_raw`,
`sg_get_config`) and `sdparm`. SPC-3 r23 §6.9, Table 98: MODE SENSE's PC field
returns current (00b), **changeable (01b, a mask)**, default (10b) or saved
(11b) values. Saved values fail with SAVING PARAMETERS NOT SUPPORTED when not
implemented [spec]. A changeable bit means the drive *accepts* a value. **It
does not mean the drive acts on it**; see Pioneer below.

### 2a. Read/Write Error Recovery mode page (01h)

- Layout (MMC-6 r02g §7.3.2, Table 662; MMC-3 r10g §6.3.4, Table 344) [spec]:
  - byte 2 holds AWRE, ARRE, TB, RC, *Reserved*, PER, DTE, DCR;
  - byte 3 is the Read Retry Count;
  - byte 7 is EMCDR (MMC-5 and later);
  - byte 8 is the Write Retry Count.
- **EER is not an MMC bit.** Bit 3 is Reserved in MMC. EER comes from the disk
  command set (SBC); MMC-6 names it only in passing, in the RC text [spec].
- **TB = 1**: a block not recovered within limits is sent to the host before
  CHECK CONDITION [spec, MMC-6 §7.3.2.5.3].
- **RC = 1**: "the Drive shall transfer the entire requested length of data
  without adding delays to perform error recovery procedures. This implies that
  the Drive may send data that is erroneous or fabricated … This bit may be used
  in image processing, audio, or video applications." RC takes priority over
  the other error bits [spec, MMC-6 §7.3.2.5.4]. A drive left at RC = 1 is
  *permitted by the standard* to fabricate audio.
- **PER**: report recovered errors. "For CD media this capability is used only
  to report when the Layered Error correction has been used". That makes it a
  data-sector (L-EC) concept. CD-DA has no L-EC [spec, MMC-6 §7.3.2.5.5;
  MMC-3 §6.3.4].
- **DTE** stops the transfer on a recovered error. **DCR** disables ECC
  [spec, MMC-6 §7.3.2.5.6-7].
- **The CD error-recovery codes (Table 345 / Table 663) are written for CD-ROM
  sectors** in terms of CIRC versus L-EC. MMC states no CD-DA-specific
  behaviour [spec]. What any drive does with these bits on audio is not
  specified by MMC.
- **Which drives honour the bits**:
  - **Pioneer BDR-203/BDC-203: "The AWRE and ARRE bits are not supported and
    are ignored. The TB, RC, DTE and DCR bits are ignored. The PER bit and
    EMCDR field are used to control the defect reporting. Setting value of the
    Read Retry Count and the Write Retry Count field are ignored."**
    [vendor doc, §4.12.2.2]. PS is not supported, so nothing is saved
    [§4.12.2].
  - dvdisaster sets 01h byte 2 to `0x20` (TB) by default, or `0x21`
    (TB+DCR), plus a retry count. It verifies by reading the page back
    [src speed47/dvdisaster@0137b61:src/scsi-layer.c:1578-1716; src/closure.c:557].
    Its manual: mode 20 "makes the drive apply its built-in error correction
    to the best possible extent before transferring a defective sector", and
    "some drives can only read defective sectors using mode 21"
    [src dvdisaster.en.1:418-426]. That is evidence that *some* drives act on
    TB/DCR **for CD data sectors**. For CD-DA it is not established for any
    named drive.
  - DiscImageCreator only *logs* page 01h: DCR, PER, EER, RC, TB, ARRE, AWRE,
    ReadRetryCount [src DiscImageCreator@9269234:DiscImageCreator/outputScsiCmdLog.cpp:3157-3188].
  - libcdio-paranoia and cdda2wav never send MODE SELECT for page 01h (grep).

### 2b. Caching mode page (08h), RCD

- MMC-6 §7.5, Table 675 [spec]: RCD = 1 means "the Drive shall transfer all of
  the data requested by a READ command from the medium". With READ(12)'s
  Streaming bit set, "the WCE and RCD bits … may be ignored" (§6.15.2.6).
- **Pioneer BDR-203: "The Caching Page is supported for compatibility of other
  CD-R/RW drive. This page has no effect on write/read operation."**
  [vendor doc, §4.12.2.1].
- CacheExplorer's "Testing cache disabling" measures whether the bit works. On
  a LiteOn LH-20A1P it printed "not supported" [forum, dBpoweramp thread with
  cachex 0.8 output].
- Whether CD, DVD or BD drives generally honour RCD for CD-DA: not
  established. The two data points are "no effect" (Pioneer, by documentation)
  and "not supported" (one LiteOn, by test).

### 2c. READ CD: C2 error field, block error byte, DAP; page 2Ah bits

- READ CD error field (MMC-3 r10g §5.17, Table 150; MMC-6 §6.19.2.7, Table 355)
  [spec]:
  - 01b: 294 bytes, one bit per byte of the 2352-byte sector;
  - 10b: block error byte (the OR of all C2 bits), a pad byte, then the 294
    bytes;
  - "If the Logical Unit does not support the C2 pointers, and the Error field
    is not zero, the C2 data field shall be zero filled" (MMC-3). **A drive
    without C2 can return zeros, so a clean C2 field from it proves nothing.**
- **DAP** (READ CD byte 1 bit 1, MMC-5 r04 §6.20.2.3; MMC-6 r02g §6.19.2.3)
  [spec]: "If the data being read is CD-DA and DAP is set to zero, then the
  user data returned to the Host **should not be modified by flaw obscuring
  mechanisms such as audio data mute and interpolate**. If … DAP is set to one,
  then the user data … should be modified by flaw obscuring mechanisms." Support
  is declared by the DAP bit, byte 4 bit 7, of the **CD Read feature 001Eh** in
  GET CONFIGURATION (MMC-6 §5.3.8, Table 109). The same byte holds **C2 Flags**
  (bit 1) and CD-Text (bit 0) [spec]. "Should" is not "shall".
- What we send now:
  - libcdio's Linux audio path is `read_audio_sectors_linux()` →
    `mmc_read_sectors(…, CDIO_MMC_READ_TYPE_CDDA, …)`. Byte 1 is `1<<2`
    (CD-DA, DAP 0), byte 9 is `0xf<<3`, no C2 and no sub-channel
    [src libcdio@5d226a6:lib/driver/gnu_linux.c:954-961; lib/driver/mmc/mmc.c:1229-1253; include/cdio/mmc.h:514-515,552-555].
  - libcdio-paranoia reads through `cdio_read_audio_sectors()`
    [src libcdio-paranoia@384f4da:lib/cdda_interface/cddap_interface.c:89].
  - cyanrip's own READ CD calls also pass DAP false: the data-sector read
    [src cyanrip@4ebfb53c:src/cyanrip_main.c:1430] and the pregap Q read
    [src cyanrip@4ebfb53c:src/pregap.c:200-212].
  - **So the host already asks, by the standard, for unconcealed audio.**
- Page 2Ah (MMC-3 r10g §6.3.11) [spec]:
  - "C2 Pointers Supported … shall support reading C2 Error Pointers and C2
    Block Error flags via the READ CD command."
  - "CD-DA Stream is Accurate … shall support an audio location without losing
    place to continue the READ CD command … If 1, the Logical Unit can continue
    from a loss of streaming condition and no error shall be generated."
  - **MMC-6 Annex E.9: "The MM Capabilities and Mechanical Status mode page is
    read only. This mode page is legacy and was most recently defined in
    MMC-3."** Accurate Stream exists only in that legacy page; MMC-5/6 have no
    feature bit for it [spec].
- Pioneer documents the same declaration pattern our rig drive gives. The
  BDR-203's page 2Ah defaults have **C2 Pointers Supported = 0** and **CDDA
  Stream Accurate = 1** [vendor doc, §4.12.2.6 Table 35]. The same section says
  "The Current Read Speed filed does not reflect the actual read speed"
  (§4.12.2.6).

### 2d. FUA in READ(10)/READ(12)

- MMC-6 §6.14.2.3 [spec]: FUA = 1 means "The READ (10) command shall access
  the specified logical blocks from the media (i.e., the data is not directly
  retrieved from the cache)". READ(12) is §6.15. **READ CD (BEh) has no FUA
  bit** (MMC-6 Table 351), so an audio rip through READ CD cannot ask for FUA
  per read.
- dBpoweramp's "FUA Cache Invalidate" issues FUA reads to flush the drive's
  audio cache. Spoon: "mainly it is for plextors only", and "If it is set and
  your drive does not support it … it makes the rip less secure … The safe
  option is to uncheck it" [forum, 2007 and 2018].
- CacheExplorer on a LiteOn LH-20A1P printed "Supported read commands: BEh
  A8h(FUA) 28h(FUA) D4h(FUA) D5h(FUA) D8h(FUA)" and "Plextor flush command:
  accepted" [forum].
- daefeatures lists "PLEXTOR PX-W4824A (no Cache with EAC.exe -usefua)" [db].
- For our case: libcdio-paranoia does not use FUA (grep). Pioneer's BDR-203
  reference documents nothing about FUA on READ(10)/(12) beyond "If the
  Streaming bit … is set to one, the FUA bit shall be set to zero"
  [vendor doc, §4.14].

### 2e. SET CD SPEED, SET STREAMING, GET PERFORMANCE

- SET CD SPEED (BBh, MMC-6 §6.39) [spec]:
  - "provides A Host with a method to select a **preferred** physical speed";
  - a Drive Read Speed of 0000h-FFFEh "specifies a minimum read speed required
    by the Host";
  - "Once the Drive has selected a speed, that speed shall be maintained until
    the current medium is removed."
  - Support is declared by the SCS bit of the Real Time Streaming feature
    0107h (§5.3.39).
- SET STREAMING (B6h) is §6.41, and GET PERFORMANCE (ACh) is §6.7: performance
  descriptors, the drive's own nominal figures [spec].
- Linux path:
  - libcdio's Linux `set_speed` is `ioctl(fd, CDROM_SELECT_SPEED, speed)`
    [src libcdio@5d226a6:lib/driver/gnu_linux.c:1422-1426,1745].
  - The kernel's `sr_select_speed()` sends SET CD SPEED with read speed =
    N×177 kB/s, or FFFFh for 0 [src linux master, fetched 2026-11-04:drivers/scsi/sr_ioctl.c:421-443].
  - libcdio-paranoia calls `cdio_set_speed()`
    [src libcdio-paranoia@384f4da:lib/cdda_interface/cddap_interface.c:66].
- **Pioneer BDR-203:**
  - SET CD SPEED: "The drive can not specify the reading speed by any Packet
    command. The setting of Logical Unit Read Speed field is ignored. The
    reading speed is determined by the drive." [vendor doc, §4.20];
  - SET STREAMING: "The Drive can not specify the reading speed by any Packet
    command. The reading speed may be automatically reduced by the drive in
    order to retry to read a block which has not been corrected errors."
    [vendor doc, §4.21.1].
- Spoon on a Pioneer BDR-XD05: "It is the drive which decides the speed to
  use." [forum].
- Whether the BDR-209D honours SET CD SPEED's read speed is not established.
  **cyanrip's `Speed:` value says `8x` whenever the command succeeds**
  [src cyanrip@4ebfb53c:src/drive_caps.c:102-114]. On a drive that accepts and
  ignores the field, that is a nearly-true claim (see Options).

### 2f. Sub-channel selection

- MMC-3 r10g §5.17, Table 151 [spec]: 000b none; 001b RAW P-W, "not
  de-interleaved", Optional; 010b formatted Q (16 bytes, Table 152), Optional;
  100b R-W, which "may" be de-interleaved and corrected, raw, or zero-padded,
  depending on page 2Ah bits.
- The MMC-5 r04 (Table 367) and MMC-6 r02g (Table 356) drafts list only 000b,
  010b and 100b in their tables as extracted. They still define the "RAW P-W
  Sub-channel" format (MMC-5 §6.20.3.2.2: "the 96 bytes of sub-channel returned
  in the order received from the disc surface") [spec]. Whether 001b was
  dropped or the row was lost in extraction was not checked further.
- The standard does not say whether a drive's formatted Q (010b) is the
  disc's Q, or a Q the drive has repaired or synthesised. Not established for
  any drive.
- cyanrip's pregap code asks for 010b [src cyanrip@4ebfb53c:src/pregap.c:207].

## 3. Vendor features by maker

| Maker / family | C1/C2 scan support (tool, platform) | Read-error or read-speed vendor settings | C2 and overread, community view |
|---|---|---|---|
| **Pioneer** DVR-106…112 (+ ASUS DRW-xxxxP, TEAC DV-W5xD, Plextor PX-810 rebadges) | QPxTool Pioneer plugin, Linux: BLER + E22, **CU hard-coded 0** [src qpxtool@8cf1003:plugins/pioneer/qscan_cmd.cpp:149-157]; ODC disc quality DVR-103…117, Windows [vendor doc, ODC FAQ] | PureRead (§1); QuietMode/speed limit via 3Ch/BBh (§1) [src]; ODC "Drive status" shows temperature and laser current on Pioneer drives (Windows) [vendor doc, ODC manual §16] | — |
| **Pioneer BD** (BDR-2xx, S0x, XD0x) | Not in QPxTool's SupportedDevices. A wildcard row `{"PIONEER ", DEV_PIONEER, "", PIO_DVR_112, CHK_ERRC_CD \| CHK_ERRC_DVD}` makes QPxTool *treat any Pioneer as a DVR-112* [src qpxtool@8cf1003:plugins/pioneer/qscan_plugin.h:34]. Untested on BD; it sends WRITE BUFFER `3Bh` mode 02h buffer `E1h` [qscan_cmd.cpp:61-64]. ODC: no Pioneer BD in its list [vendor doc] | as above | Page 2Ah: C2 0, Accurate Stream 1 (BDR-203 defaults) [vendor doc]. CUERipper tries C2 mode 296 first for BDR-UD04, BDR-XD05, BDR-XD07U and DVR-S21, where "Mode294 does not work" [src cuetools@f2ec334:CUETools.Ripper.SCSI/SCSIDrive.cs:821-844]. dBpoweramp's BDR-X13UBK: "detection … yield null results" for C2 [forum]. AccurateRip offset +667 for all BDR-209 variants [db] |
| **Plextor** CD-R Premium/Premium2, PX-W4012/W5224/W4824, PX-708…760 | QPxTool Plextor plugin (Q-Check `EAh`): BLER, E11, E21, E31, E12, E22, E32, UNCR [src qpxtool@8cf1003:plugins/plextor/qscan_cmd.cpp:248-265; lib/qpxtransport/include/qpx_opcodes.h:130-133]; ODC CD Bler on Premium and PX-712/714/716 [vendor doc] | `E9h` PLEXTOR_MODE: SpeedRead on/off; Silent mode with max CD **read** speed 4-48× and access slow/fast; SecuRec; GigaRec/VariRec (writing) [src qpxtool@8cf1003:console/cdvdcontrol/cdvdcontrol.cpp:259-301; lib/qpxplextor/plextor_features.cpp:524-599]. FUA cache flush ("mainly … plextors") [forum] | Raw read `D8h` READ CDDA with C2 + sub [src redumper@fa5d243:scsi/mmc.ixx:33; cd/cd_common.ixx:469]. redump: the "Good Plextors" are "unique in their ability to fully dump the lead-in … all 150 sectors"; PX-W4824 only 75 sectors of pregap [wiki]. HA wiki: C2 reliable on "typically old models by Plextor" [wiki] |
| **LiteOn / PLDS / Slimtype / Sony DW- and DRU- (LiteOn OEM) / TEAC DV-W5xG** | QPxTool LiteOn plugin (`DFh` old method: BLER, E22, **E32**; `F3h` new method: BLER, E22) [src qpxtool@8cf1003:plugins/liteon/qscan_cmd.cpp:245-297]; KProbe (Windows); ODC (MediaTek LiteOn) [vendor doc] | None found for read-error handling | MediaTek BD drives (MT1959/MT1939) with the `F1h` cache read can read into the lead-out under redumper [wiki, redump]. Gough: MediaTek C1 figures look optimistic; C2 more consistent across drives [forum, 2025] |
| **BenQ** DW1620/1625/1640/1650/1655 | QPxTool BenQ plugin: full CIRC incl. E32 [src qpxtool@8cf1003:plugins/benq/qscan_cmd.cpp:373-377]; ODC CD Bler [vendor doc]; Gough uses the DW1640 as his reference CD scanner [forum] | None found | — |
| **NEC / Optiarc** ND-35xx/45xx, AD-71xx/72xx | QPxTool NEC plugin (`F3h`): BLER, E22 [src qpxtool@8cf1003:plugins/nec/qscan_cmd.cpp:80-100]; ODC [vendor doc] | None found | dBpoweramp 2024 "worst drives" list holds ND-3520A/3530A/3550A/2500A/2510A (93.5-94.9 %) [db]. redumper lists several NEC/Optiarc as good only with a modified "seri" firmware [src redumper@fa5d243:drive.ixx:198-208, vendor string "seri-01 BT-LIGGY"] |
| **ASUS** (MediaTek DRW-1612…2014L1; BW-16D1HT) | QPxTool ASUS plugin: BLER, E22 [src qpxtool@8cf1003:plugins/asus/qscan_cmd.cpp:74-90] | None found | BW-16D1HT 3.02 is in redumper's good list (MTK3) [src redumper@fa5d243:drive.ixx:168] |
| **LG / HL-DT-ST** | No QPxTool plugin. ODC: "LG drives are not supported" [vendor doc] | None found | redumper good list: BU40N 1.00, BH16NS55 1.02, WH14NS40 1.03, BH16NS40 1.03 and others on named firmware [src redumper@fa5d243:drive.ixx:167-192]. Bad: WH16NS40 1.05 and WH16NS60 1.02, "scrambled" [src redumper@fa5d243:drive.ixx:240-241]. redump: JB8/JB9 platforms lost `F1h` in later firmware; OmniDrive firmware restores lead-out reading [wiki] |
| **Samsung / TSST** | QPxTool TSST plugin, SH-S202N only: BLER, E32 [src qpxtool@8cf1003:plugins/tsst/qscan_plugin.cpp:54-59] | None found | TS-H352C "supports C2 only on data" [src redumper@fa5d243:drive.ixx:238]. TS-H353C/SH-D163C need MoriGM's patched "ZZ00" firmware [wiki, redump] |
| **Generic (any drive with C2)** | QPxTool "C2P" plugin: READ CD with byte 9 = `0xFA`; counts set C2 bits as "E22" and **any failed READ CD as "UNCR"** [src qpxtool@8cf1003:plugins/generic/qscan_cmd.cpp:57-80] | — | On a drive without C2 the field is zero-filled (MMC-3), or the command fails and is counted as UNCR. **Meaningless on the BDR-209D.** |

Community ratings worth knowing, and what each measures:

- **redumper** calls a drive good "if it supports subcode and C2 error
  pointers, can read scrambled data sectors, at least 75 sectors of lead-in and
  at least 75 sectors of lead-out" [src redumper@fa5d243:drive.ixx:142].
- **redump wiki** gives the same requirements, plus "Reliable C2 error pointers
  support" [wiki].
- **daefeatures.co.uk** has per-drive Accurate Stream, Caching, C2, HTOA and
  Overread columns. For every BDR-209 variant only the +667 offset imported
  from dBpoweramp is filled [db].
- **AccurateRip drive offsets**: "PIONEER - BD-RW BDR-209D +667, submitted by
  1082, 100%" [db].
- **dBpoweramp "CD Drive Accuracy 2024"**: "PIONEER - BD-RW BDR-209D (442
  users): Submissions: 17328 accurate, 328 inaccurate, 98.1423 % accuracy".
  - Method: "lowest % inaccurate tracks, on the basis that people who have a
    drive would have the same number of damaged disks as everyone else, on
    average".
  - For comparison: BDR-209M 98.88 %, BDR-S09 99.34 %, BDR-S11JX 99.49 %,
    Plextor PX-716A 98.10 % [db].
  - This rates AccurateRip outcomes, with disc condition as a confound. It
    does not rate C2.
- **EAC's two C2 tests**: "Detect Read Features" "only tests if the drive says
  it can provide C2 error information". "Examine C2 Feature" "tests whether the
  drive can actually report an uncorrectable error". "Neither test can be used
  to determine whether all uncorrectable errors are reported" [wiki, HA EAC
  Drive Options].
- **dBpoweramp's C2 detection** "rips the same as ripping with c2 enabled, so
  it relies on the drive returning c2 data" [forum, Spoon, 2025].

## 4. Disc-quality scanning: could a scan show the error at track 5, 02:24:59?

Tools and platforms:

- **QPxTool** (GPL; `qscan -t errc`, or the GUI) is the only open-source C1/C2
  scanner found that runs on Linux.
- KProbe (LiteOn), Nero CD-DVD Speed and Opti Drive Control (ODC) run on
  Windows.

What each tool reports:

- **QPxTool**: per block, LBA | speed | BLER | E11 E21 E31 | E12 E22 E32 | UNCR
  [src qpxtool@8cf1003:lib/qpxscan/qpx_scan_algo.cpp:488-503]. The CLI prints
  each line with `\r`, so redirect it to a file to keep every interval. It has
  no range option; the GUI has one [src console/qscan/qscan.cpp:196-218].
- **ODC**: "C1: total number of errors at the C1 stage; C2: number of
  uncorrectable errors at the C2 stage … The errors are measured and shown for
  every second (75 sectors)". Its "CD Bler" test, with E11 through E32, works
  only on BenQ DW1620/1640/1650/1655 and Plextor PX-716 [vendor doc, ODC
  manual §9-10].

Drive families that can report C1/C2/CU per position under Linux:

- Plextor Premium and PX-708…760: E32 and UNCR.
- BenQ DW16xx: E32.
- LiteOn DVD writers on the old method: E32.
- NEC/Optiarc, ASUS, TSST and Pioneer DVR: BLER and E22 only, no CU.

**Could a scan show it?** Yes, as a count in the one-second interval containing
the spot, on a drive that reports E32 (CU). Four caveats:

- **Address it as an absolute LBA.** If 02:24:59 is track-relative mm:ss:ff,
  the spot is track 5's start LBA + 10 859.
- **The rip's sample position includes the +667-sample (≈1.13-sector) read
  offset correction.** A scan addresses raw sectors, so near an interval
  boundary the matching interval can be the next one.
- **Results differ between drives and speeds** [forum, Gough 2025: "significant
  differences in scanning results across drives and speeds"]. Scan at two
  speeds on two families.
- **What each result shows.** A CU at that second corroborates "the drive saw a
  frame it could not correct and concealed it". No CU does *not* exclude an
  undetected CIRC miscorrection, or a drive-specific misread. A clean scan on
  several drives, plus a correct rip on another drive, points away from the disc.

**On the BDR-209D itself a scan is low-value and of unknown risk.**

- QPxTool's Pioneer plugin would claim the drive through its wildcard row and
  send DVR-era vendor commands (WRITE BUFFER `3Bh` mode 02h, READ BUFFER `3Ch`
  buffer `E1h`). These are untested on a BD drive, and they report CU = 0
  always.
- The generic C2P plugin needs C2 pointers, which the drive does not declare.
- Pioneer's own "Audio CD check" (grades A-D) exists on the BDR-S09J-X and
  BDR-S11J-X only [vendor doc, press release 2015-01-08; BDR-211JBK comparison
  table].

## 5. What other rippers log about drive state

**Of the drive-related header fields, only the drive identity, plus whipper's
CD-R detection, XLD's media type and CUERipper's chosen read command, come from
the drive at rip time.** Nearly everything else is a user setting, sometimes
chosen with the help of an earlier test. Some fields are printed as constants.

| Ripper | Field | Where the value comes from | Source |
|---|---|---|---|
| EAC | `Used drive` | INQUIRY (drive's declaration) | [forum] log examples |
| EAC | `Read mode`, `Utilize accurate stream`, `Defeat audio cache`, `Make use of C2 pointers` | **User settings** in Drive Options. "Detect Read Features" suggests them; the log shows the setting in use, not the test result | [wiki] HA EAC Drive Options |
| EAC | `Read offset correction`, `Overread into Lead-In and Lead-Out`, `Fill up missing offset samples with silence`, `Delete leading and trailing silent blocks`, `Null samples used in CRC calculations`, `Used interface`, `Gap handling` | User settings. Gap *detection* is a measurement; `Gap handling` is the chosen treatment | [wiki], [forum] |
| EAC | per track: `Peak level`, `Extraction speed`, `Range/Track quality`, `Copy CRC`/`Test CRC`, `Suspicious position 0:01:30 - 0:01:31` | **Measured** during the rip; positions at 1-second resolution | [forum] whipper issue 75 quoting an EAC log |
| dBpoweramp | `Ripping with drive '…'` | INQUIRY | [forum] |
| dBpoweramp | `Drive offset`, `Overread Lead-in/out`, `AccurateRip: Active`, `Using C2`, `Cache: 1024 KB`, `FUA Cache Invalidate`, `Pass 1/2 Drive Speed`, `Ultra::` and `Bad Sector Re-rip::` | **Settings.** Cache, C2 and FUA can be set from detect buttons, which measure by timing or by ripping. `Drive Speed: Max` is the request; "It is the drive which decides the speed" | [forum] logs incl. a BDR-208D and a BDR-UD04 |
| dBpoweramp | per track: `Ripped LBA x to y … in 0:35`, AccurateRip result, `Insecure Audio from 00:02:44.760 to 00:02:44.773`, `Re-rip Frame: 212409 (00:02:42,426). Insecure (c2 dropped 10)` | **Measured**, per frame, with LBA and time | [forum] |
| XLD | `Used drive : X (revision Y)`, `Media type : Pressed CD` | Drive and disc, at rip time | [forum] logs |
| XLD | `Ripper mode`, `Make use of C2 pointers : NO`, `Read offset correction`, `Max retry count`, `Gap status : Analyzed, Appended` | Settings, plus the analysis result for gaps | [forum] |
| XLD | `Disable audio cache : OK for the drive with a cache less than 1375KiB` | **A bounded claim about the method, not a measurement of this drive**: the model to copy | [forum] |
| whipper | `Drive: vendor model (revision)` | INQUIRY | [src whipper@71251a0:whipper/result/logger.py:39-40] |
| whipper | `Defeat audio cache: true` | **Stored in config from an earlier `cd-paranoia -A` analysis**, not measured at rip time | [src whipper/result/logger.py:43; whipper/command/cd.py:186-189; whipper/program/cdparanoia.py:588-627] |
| whipper | `Read offset correction`, `Overread into lead-out`, `Gap detection: cdrdao <ver>` | Config, setting, tool version | [src logger.py:44-51] |
| whipper | `CD-R detected` | **Measured** at rip time by cdrdao | [src logger.py:53; cd.py:142] |
| CUERipper (EAC-format log) | `Utilize accurate stream : Yes`, `Defeat audio cache : Yes`, `Make use of C2 pointers : No`, `Overread … : No`, `Used interface : Native Win32 interface for Win NT & 2000` | **Hard-coded strings, the same for every drive** | [src cuetools@f2ec334:CUETools.Processor/CUESheetLogWriter.cs:104-126] |
| CUERipper (own log) | `Read command : BEh, F8h+C2…, N blocks at a time` | **Measured** by probing which READ CD form and C2 mode the drive accepts | [src CUESheetLogWriter.cs:272-275; CUETools.Ripper.SCSI/SCSIDrive.cs:171-182,809-866] |

## Table: settings and capabilities

| Setting | Standard or vendor | Drives | Readable over SCSI on Linux | Settable | Effect on CD-DA reads | Source |
|---|---|---|---|---|---|---|
| PureRead mode (Standard/Master/Perfect) | Vendor (Pioneer) | Pioneer DVR-115D on; BDR retail lines (PureRead2 to 4+); **BDR-209D not established**, and a firmware census says 1.51 reports it unsupported | Yes, by Pioneer's vendor READ BUFFER `3Ch` mode `02h` buffer `F4h`: support at byte 9, mode at bytes 4-5 | Pioneer BD Drive Utility (Windows); `pioneer-optical`'s WRITE BUFFER `FAh` encoding; saved in drive only on "+" models | Standard interpolates; Master retries then interpolates; Perfect retries then aborts the read | [vendor doc] manual, vol. 17/27; [src] pioneer-optical, QPxTool stub |
| Real Time PureRead | Vendor | PureRead3 and later | No | Drive Utility | Retries during real-time playback, interpolates on missed deadline | [vendor doc] |
| QuietMode / speed limit | Vendor | Pioneer DVR-A09-era; reported working on BDR-UD04 | Yes: READ BUFFER 3Ch/01h/F4h | Yes: SET CD SPEED BBh vendor bits, save bit | Caps CD read at 24× (limit on) | [src] QPxTool; [forum] MakeMKV |
| Error recovery page 01h: AWRE, ARRE, TB, RC, PER, DTE, DCR | Standard (MMC) | All MMC drives expose it | Yes: MODE SENSE(10) page 01h, PC 00/01/10/11 | MODE SELECT(10); **ignored by Pioneer BDR-203 except PER** | MMC defines CD-ROM cases only; RC = 1 permits "erroneous or fabricated" data | [spec] MMC-6 §7.3.2; [vendor doc] BDR-203 §4.12.2.2 |
| Read Retry Count | Standard | as above | Yes | MODE SELECT; **ignored by BDR-203** | Number of recovery attempts | [spec]; [vendor doc] |
| EER | Not in MMC (SBC bit) | — | Bit 3 reserved | — | — | [spec] MMC-6 Table 662 |
| RCD (page 08h) | Standard | All MMC drives that expose 08h | Yes | MODE SELECT; **"no effect" on BDR-203** | Should force media reads | [spec] MMC-6 §7.5; [vendor doc] §4.12.2.1 |
| FUA on READ(10)/(12) | Standard, per command | Plextor (cache flush); LiteOn LH-20A1P accepted | n/a (per command) | Per command | Not on READ CD; used as a cache-flush trick | [spec] MMC-6 §6.14.2.3; [forum] |
| DAP bit in READ CD | Standard (MMC-5/6), per command | Declared by feature 001Eh DAP | Yes: GET CONFIGURATION 001Eh | Per command; libcdio sends 0 | DAP 0: data "should not be modified by … mute and interpolate" | [spec] MMC-6 §6.19.2.3, §5.3.8; [src] libcdio |
| C2 error pointers (READ CD error field) | Standard | Declared by page 2Ah (legacy) and 001Eh C2 Flags | Yes, both declarations | Per command | Per-byte C2 flags; zero-filled when unsupported; reliability varies by drive | [spec] MMC-3 §5.17, MMC-6 §6.19.2.7; [wiki] |
| CD-DA Stream is Accurate | Standard, legacy (MMC-3 only) | page 2Ah | Yes | No (read-only page) | Restart without losing place | [spec] MMC-3 §6.3.11; MMC-6 E.9 |
| Read speed (SET CD SPEED / SET STREAMING) | Standard | SCS bit in feature 0107h | GET PERFORMANCE (nominal); page 2Ah current speed "does not reflect the actual read speed" on BDR-203 | BBh / B6h; **read speed ignored by BDR-203** | Slower reads usually reduce errors (ODC manual); the drive also slows itself on errors | [spec] MMC-6 §6.39, §6.41, §6.7; [vendor doc] |
| Sub-channel selection 001b / 010b / 100b | Standard | 001b optional in MMC-3 | Per command | Per command | 010b returns formatted Q; provenance of that Q not specified | [spec] MMC-3 Table 151; MMC-5 Table 367 |
| Plextor SpeedRead, Silent mode (max CD read speed), SecuRec | Vendor (E9h) | Plextor PX-7xx, Premium | Yes (QPxTool) | Yes | Silent mode caps read speed | [src] QPxTool |
| Plextor Q-Check C1/C2 | Vendor (EAh) | Plextor Premium, PX-7xx | Yes (measurement) | — | None (measurement only) | [src] QPxTool |
| LiteOn/NEC/BenQ/TSST/ASUS error counters | Vendor (DFh, F3h, …) | See §3 | Yes (QPxTool) | — | None (measurement only) | [src] QPxTool |
| D8h READ CDDA | Vendor (legacy Pioneer/Plextor) | Plextor CD-R and PX-7xx | n/a | Per command | Raw CD-DA + sub + C2 | [src] redumper, DIC |
| F1h cache read (lead-out) | Vendor (MediaTek) | MT1959/MT1939 BD drives on named firmware | Per command | Per command | Lead-out overread | [wiki] redump |

## Options for us

Anything below that changes a log line, the CLI or drive I/O is handshake
material and needs hardware verification (CLAUDE.md). These are proposals, not
decisions.

### What cyanrip could log

The rule throughout: log what was observed, labelled by provenance, and never
a value it did not observe.

1. **Keep `C2 errors:` and `Accurate stream:`**, and add their twin
   declaration from GET CONFIGURATION. Feature **001Eh**, byte 4, holds DAP
   (bit 7), C2 Flags (bit 1) and CD-Text (bit 0). Feature **0107h** holds the
   SCS bit. Label them "declared by drive (GET CONFIGURATION feature 001Eh)".
   - Two declarations can disagree. That is information, and not a reason to
     pick one.
   - cyanrip already fetches a 500-byte all-features reply
     [src cyanrip@4ebfb53c:src/cyanrip_main.c:385-389]. On a BD drive that may
     not reach 0107h. A request with RT=10b and starting feature 001Eh (then
     0107h) returns exactly one feature each.
   - The capabilities page is legacy (MMC-6 E.9). That belongs in our docs; it
     does not need a log word.
2. **Log the audio read request, as a fact about our code, not about the
   drive.** Say "READ CD (BEh), sector type CD-DA, DAP 0, no C2, no
   sub-channel, via libcdio `cdio_read_audio_sectors`". This is true by
   construction. Under MMC-5/6 it is the host asking for unconcealed audio, so
   any concealment the drive does is the drive's choice. It mirrors
   CUERipper's `Read command` line.
3. **Declared mode-page state, never "applied".**
   - Dump page 01h (byte 2 bits and Read Retry Count) and page 08h (RCD), each
     current (PC 00b) and changeable (PC 01b), as "declared by drive (MODE
     SENSE), effect not measured".
   - The one value worth flagging is **RC = 1** (MMC-6: the drive "may send
     data that is erroneous or fabricated").
   - Do **not** MODE SELECT these by default. Pioneer documents ignoring them,
     and a changed page is a changed drive state that other tools inherit.
4. **`Speed:`, proposed wording change (needs a round).**
   - With `-S N`, write "N× requested, accepted by drive (read speed not
     measured)" rather than `Nx`. Pioneer's BDR-203 reference says the read
     speed field is ignored.
   - Add a **measured** throughput per track, from sectors read and wall time.
5. **Sense data on read errors (measured).**
   - When a READ CD fails, log sense key, ASC and ASCQ, and the information
     field (LBA). Perfect mode, or any drive refusing to conceal, should
     surface there.
   - libcdio records the sense of the last SG_IO command and exposes it as
     `mmc_last_cmd_sense()`
     [src libcdio@5d226a6:lib/driver/gnu_linux.c:1289-1299; lib/driver/mmc/mmc.c:1100].
     cyanrip does not call it today.
   - Caution: by paranoia's callback another command may have overwritten it.
     Capturing it reliably needs a read wrapper.
6. **PureRead only as the drive answers it, never the operator's setting.**
   On a drive whose INQUIRY vendor is `PIONEER`, the 256-byte block READ
   BUFFER `F4h` returns, kept raw, with byte 9 and bytes 4 and 5 read from it.
   It is a vendor command, read-only, so whether to send it is a decision for
   the round. The operator's setting is an operator statement with its own
   provenance (see below), not a drive measurement.
7. **Per-read latency near trouble (measured).**
   - PureRead's retries cost milliseconds each and up to tens of seconds per
     spot (Pioneer vol. 27).
   - The maximum READ CD latency per track is a cheap, honest signal that the
     drive retried, even when the data it returned is identical.
   - libcdio's default MMC timeout is 6000 ms
     [src libcdio@5d226a6:include/cdio/mmc_util.h:138]. A long drive-side retry
     can exceed it, and the stall watchdog should name that case.

### What the rig sessions should record

- **The drive**:
  - INQUIRY vendor, product and revision;
  - `sg_get_config -v` (full feature list);
  - `sg_modes -a -c 0`, `-c 1`, `-c 2` and `-c 3` (all pages; current,
    changeable, default, saved). Saved values may fail, and that failure is
    itself a datum.
  - These are read-only. Each output is evidence and is filed through the
    evidence tools.
- **The PureRead claim, with provenance**:
  - whether the Pioneer Drive Utility recognised the BDR-209D, and which
    utility version;
  - which options it showed: an on/off box, Master/Perfect, and "Save settings
    to drive" (expected absent on PureRead2);
  - screenshots;
  - the UTC time the setting was made;
  - **every power loss of the drive between setting and rip** (cold boot, move
    between hosts, cable change);
  - the host and OS of each step.
  - Record the setting as "set by operator via utility", never as observed.
- **The MODE SENSE dump again after the utility change.** Diff it against the
  previous dump.
  - A changed byte, perhaps in a page DiscImageCreator would log as
    "VENDOR_SPECIFIC", localises where PureRead lives.
  - No change says it is not in a mode page.
- **A targeted behavioural read of the bad spot** under each mode the utility
  offers. Read the same sectors around track 5 02:24:59 N times, recording:
  - per read, the data hash;
  - the latency;
  - any sense data.

  Expected signatures, a hypothesis to test rather than a fact:

  | Mode | Data | Latency | Sense |
  |---|---|---|---|
  | Standard | identical wrong samples | fast | none |
  | Master | identical or different samples | slow | none |
  | Perfect | — | slow | MEDIUM ERROR, or a timeout, at the LBA |

  If all modes give the same fast identical data, then either PureRead is
  absent or not retained, or the drive does not see the frame as
  uncorrectable.
- **Disc state**: cleaned or not and when, plus the same AccurateRip/CTDB
  identifiers as the rip.
- **Speeds**: the requested speed, and the measured throughput.

### Tests that give the most diagnostic data, ranked

1. **Behavioural PureRead test on the rig drive** (above). No new tools.
   Directly tests Platterpus's hypothesis, and costs one Windows session plus
   Linux reads. First confirm the utility offers PureRead for a BDR-209D at
   all. If it does not, that is the finding.
2. **C1/C2/CU scan of the reference disc on a drive that reports E32.**
   Candidates: Plextor PX-716A/712A/Premium, or BenQ DW1640/1650 under
   QPxTool on Linux, or ODC on Windows; a LiteOn MediaTek writer as the second
   family. Scan at a low and a medium speed and read the one-second interval
   holding the spot.
   - CU there means the disc presents an uncorrectable frame, and the rig
     drive concealed it.
   - No CU on two families points to the BDR-209D (or a miscorrection), not
     to the disc.
3. **Rip the track on a C2-reporting drive from redumper's good list.** For
   example, an ASUS BW-16D1HT on 3.02, an LG BH16NS55 on 1.02, or a Plextor
   PX-716A on 1.11. Log C2 at the spot (redumper, or EAC/dBpoweramp with C2
   on), and compare samples and AccurateRip. This separates "the disc is bad
   there" from "this drive misreads there".
4. **The drive's own answer, first, owner's decision:** READ BUFFER `3Ch`,
   mode `02h`, buffer `F4h`, 256 bytes, as `pioneer-optical` sends it:
   `sg_raw -r 256 /dev/srN 3c 02 f4 00 00 00 00 01 00 00`. Byte 9 says
   whether PureRead is supported; bytes 4 and 5 give the mode. Read it before
   and after any utility change. It is a vendor command, read direction,
   untested on a BDR-209D; never send its write counterpart.
5. **Optional, larger:** capture the Drive Utility's commands.
   - Attach the drive through a USB-SATA bridge passed into a Windows VM, and
     capture the CDBs with `usbmon` on the Linux host.
   - That is how a PureRead read or set command could be found.
   - Not established: whether the utility works over a bridge, or for a
     BDR-209D.

Do **not**:

- run QPxTool's Pioneer scan plugin on the BDR-209D (wildcard match, DVR-era
  WRITE BUFFER `3Bh` mode 02h buffer `E1h`, CU always 0);
- run the generic C2P scan on it (no C2: zero-filled data, or every failure
  counted as UNCR);
- MODE SELECT page 01h or 08h on the rig drive as a "fix". Pioneer documents
  that the drive ignores them, and the change would silently alter later runs.

## Not established

- Whether the BDR-209D (any firmware, and 1.51 in particular) implements
  PureRead, and whether the Pioneer Drive Utility v1.2.0.3 recognises a
  BDR-209D.
- The BDR-209D's default PureRead mode, and whether its setting survives a
  power cycle, a warm reboot, a bus reset or a libata error-handling reset.
- The sense key and ASC that Perfect mode returns, and how long the drive
  retries before returning it.
- What the BDR-209D answers to READ BUFFER `F4h` at run time, and whether the
  census's mapping of the `sat/8600` and `sat/8601` 1.51 images to it holds.
- Whether the BDR-209D honours SET CD SPEED's read speed, the caching page's
  RCD, or any error recovery bit (documented only for the BDR-203).
- Whether any named drive honours page 01h bits for CD-DA (dvdisaster shows
  some drives do for CD data).
- Whether the BDR-209D sets the DAP bit in feature 001Eh, and whether it
  conceals audio despite DAP 0.
- Whether QPxTool's Pioneer plugin works, or is safe, on any Pioneer BD drive.
- Whether the BDR-209D can read lead-in or lead-out. redumper's 1.10 row uses
  pregap start 0; daefeatures has no data.

## Sources

Specifications [spec], drafts at 13thmonkey.org:

- MMC-3 r10g (T10/1363-D, 2001-11-12): https://www.13thmonkey.org/documentation/SCSI/mmc3r10g.pdf
  (§5.17 Tables 150-152; §6.3.4 Tables 344-345; §6.3.11)
- MMC-5 r04 (T10/1675-D, 2006-10-24): https://www.13thmonkey.org/documentation/SCSI/mmc5r04.pdf
  (§6.20.2.3 DAP; Table 367; §6.20.3.2.2)
- MMC-6 r02g (T10/1836-D, 2009-12-11): https://www.13thmonkey.org/documentation/SCSI/mmc6r02g.pdf
  (§5.3.8 Table 109; §5.3.39; §6.7; §6.14.2.3; §6.15.2.6; §6.19.2.1-8;
  §6.39; §6.41; §7.3.2 Table 662-663; §7.5 Table 675; Annex E.9)
- SPC-3 r23: https://www.13thmonkey.org/documentation/SCSI/spc3r23.pdf (§6.9, Table 98)

Pioneer [vendor doc]:

- BDR-S13UBK owner's manual (copy at manuals.plus): https://manuals.plus/pioneer/bdr-s13ubk-internal-bddvdcd-writer-manual
- Optical disc drive development story vol. 17: https://jpn.pioneer/ja/pcperipherals/dvdrrw/story/index_17.html
- Optical disc drive development story vol. 27: https://jpn.pioneer/ja/pcperipherals/dvdrrw/story/index_27.php
- BDR-209JBK product page (PureRead2): https://jpn.pioneer/ja/support/s-product.php?main_cd=012&product_no=00006216
- BDR-209MBK (PureRead2): https://usa.pioneer/products/bdr-209mbk
- BDR-209DBK product page: https://pioneerelectronics.com/PUSA/Computer/Computer+Drives/BDR-209DBK
- BDR-2209 product overview (PureRead2, Drive Utility): https://www.bhphotovideo.com/lit_files/252557.pdf
- BDR-209DBK Product Specification Rev 1.01, 2014-01-23 (posted by Newegg): https://images10.newegg.com/UploadFilesForNewegg/itemintelligence/Pioneer/BDR_209DBK_Pro_Spec_Rev1_20011445191870512.pdf
- BDR-203/BDC-203 Command Reference Manual v1.01, 2009-02-13: https://bitsavers.trailing-edge.com/pdf/pioneer/dvd/BDR-203_BDC-203_Command_Reference_Manual_1.01_200902.pdf
  (§4.12.2, §4.12.2.1, §4.12.2.2, §4.12.2.6, §4.14, §4.15, §4.20, §4.21.1, §4.23)
- Firmware and Drive Utility downloads: https://pioneer.jp/device_e/product-e/ibs/device_e/dev00001r_e.html
- BDR-S09J-X press release, 2015-01-08: https://jpn.pioneer/ja/corp/news/press/index/1873/
- BDR-S09J-BK basic features: https://jpn.pioneer/ja/pcperipherals/bdd/products/bdr_s09j/basic.php
- BDR-211JBK page and comparison table: https://jpn.pioneer/ja/pcperipherals/bdd/products/bdr_211j/
- BDR-212JBK press release (PureRead3+): https://jpn.pioneer/ja/corp/news/press/index/2355/

Source code [src], cloned 2026-11-04:

- QPxTool upstream `git.code.sf.net/p/qpxtool/code` @ 8cf1003 (2020-11-11)
- QPxTool fork `github.com/speed47/qpxtool` @ ae6f7b4 (v0.8.1-pl8)
- pioneer-optical `github.com/MattJackson/pioneer-optical` @ d2cbbf2 (2026-11-01), read, not run
- redumper `github.com/superg/redumper` @ fa5d243
- DiscImageCreator `github.com/saramibreak/DiscImageCreator` @ 9269234
- libcdio `github.com/libcdio/libcdio` @ 5d226a6
- libcdio-paranoia `github.com/rocky/libcdio-paranoia` @ 384f4da
- whipper `github.com/whipper-team/whipper` @ 71251a0
- CUETools `github.com/gchudov/cuetools.net` @ f2ec334
- dvdisaster `github.com/speed47/dvdisaster` @ 0137b61
- schilytools (cdrtools) `codeberg.org/schilytools/schilytools` @ e835e64
- Linux `drivers/scsi/sr_ioctl.c`, master, fetched 2026-11-04 (no commit pinned)
- cyanrip (this fork) @ 4ebfb53c: `src/cyanrip_main.c`, `src/drive_caps.c`, `src/pregap.c`

Databases and wikis [db], [wiki]:

- AccurateRip drive offsets: http://www.accuraterip.com/driveoffsets.htm
- dBpoweramp "CD Drive Accuracy 2024" (Spoon, 2024-04-28): https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/324732-cd-drive-accuracy-2024
- daefeatures BDR-209 search: https://www.daefeatures.co.uk/search?accurate_stream=All&c2=All&caching=All&htoa=All&manufacturer=0&model=BDR-209&overread=All
- Redump wiki, CD compatibility: http://wiki.redump.org/index.php?title=Optical_Disc_Drives%3A_CD_Compatibility_Technical_Details
- Hydrogenaudio, EAC Drive Options: https://wiki.hydrogenaudio.org/index.php?title=EAC_Drive_Options
- Hydrogenaudio, EAC Lossless Backup: https://wiki.hydrogenaudio.org/index.php?title=EAC_Lossless_Backup
- Opti Drive Control FAQ: https://www.optidrivecontrol.com/faq.html
- Opti Drive Control manual 1.70: https://www.optidrivecontrol.com/files/OptiDriveControl.pdf

Forums, reviews and blogs [forum]:

- Spoon on PureRead (BDR-X13UBK thread, 2024-07-04): https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/326017-pioneer-drive-bdr-x13ubk-configuration-question
- DVR-115D PureRead (2007): https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/14987-pioneer-dvr-115d-with-pureread
- cdrinfo, BDR-2207 review: https://www.cdrinfo.com/d7/content/pioneer-bdr-2207-bdr-207m-bdxl-burner-review?page=2
- cdrinfo, BDR-S13U-X review: https://www.cdrinfo.com/d7/content/pioneer-bdr-s13u-x-blu-ray-recorder?page=15
- cdrinfo, BDR-XD05J and BDR-209JBK news (2014): https://cdrinfo.com/d7/content/pioneer-bdr-xd05j-and-bdr-209jbk-bd-burners-released
- ImgBurn forum, BD209M Drive Utility: https://forum.imgburn.com/topic/25142-pioneer-bd-drive-utility-settings-and-imgburn-read-function/
- kakaku.com, BDR-209XJBK bulk and PureRead: https://bbs.kakaku.com/bbs/K0000765576/SortID=20228773/
- MakeMKV forum, cdvdcontrol on BDR-UD04: https://forum.makemkv.com/forum/viewtopic.php?start=15&t=27353
- dBpoweramp FUA threads: https://forum.dbpoweramp.com/forum/dbpoweramp/music-converter/13931-trouble-ripping-with-dbpoweramp ; https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/37828-fua-cache-invalidate
- dBpoweramp thread with CacheExplorer output: https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/15377-finding-a-good-drive-it-s-impossible
- dBpoweramp, C2 corner cases (2025): https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/335219-c2-corner-cases
- dBpoweramp log examples: https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/333618-looking-for-option-to-automatically-write-the-info-error-log ; https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/19831-track-ripped-accurately-but-contains-insecure-audio ; https://forum.dbpoweramp.com/forum/dbpoweramp/cd-ripper/35356-why-does-secure-rip-some-tracks-twice-on-one-occasion-but-once-on-others
- XLD log examples: https://sourceforge.net/p/xld/tickets/358/ ; https://kb.offsec.nl/tools/apple-macos/xld/
- EAC log excerpt with suspicious position (whipper issue 75): https://github.com/whipper-team/whipper/issues/75
- CUETools "C2 Mode296 first" issue: https://github.com/gchudov/cuetools.net/issues/192
- Gough's Tech Zone, CD C1/C2 scanning (2025-08-16): https://goughlui.com/2025/08/16/notes-cd-c1-c2-error-quality-scanning-modern-vs-older-drives-software/
