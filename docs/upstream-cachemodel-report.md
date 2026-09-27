# Draft: upstream bug report for cyanreg/cyanrip

**Not filed.** This is a draft for the maintainer to review and submit; filing on
upstream's tracker is outside this repository. Platterpus's ruling (round 7,
H11) was *"yes, and I would not wait"* — if upstream picks a different value we
want to know now rather than at the next rebase.

Everything below was re-derived immediately before writing it, against the source
bytes rather than against another build. **Re-measured 2026-09-27 against a
build of upstream `f8ebf48`**, with `tests/fixtures/cdda.bin` as the image of
`tests/fixtures/basic.cue`: at `-P 0` the decoded PCM is byte-identical to the
source; at `-P 1`, `-P 2` and `-P 3` it is 0.3 % non-zero samples against the
source's 100 %; every run exits 0 with `Ripping errors: 0`. This fork's build
gave byte-identical output at the default level on the same image. **Two
corrections came out of that re-measurement:** the title said *"at any
paranoia level"*, which `-P 0` contradicts, and the reproduction compared a
WAV file with the raw `.bin`, which differs even for a correct rip because of
the WAV header and because `1.wav` is one track of two.

---

## Title

Ripping a disc image at any paranoia level above 0 returns corrupted audio and reports `Ripping errors: 0`

## Body

Since `c431d58` ("Disable paranoia's drive cache modelling for disc images"),
ripping a BIN/CUE, NRG or CDRDAO image at the default paranoia level returns
audio that does not match the source, and reports success while doing it.

Real drives are unaffected — the code path is guarded on the image driver IDs —
and `-P 0` is byte-perfect either way. It is the default-paranoia image path
only.

### What happens

`src/cyanrip_main.c`:

```c
switch (cdio_get_driver_id(ctx->cdio)) {
case DRIVER_BINCUE:
case DRIVER_NRG:
case DRIVER_CDRDAO:
    cdio_paranoia_cachemodel_size(ctx->paranoia, 1);
    break;
```

The comment above it already identifies the coupling that causes this:

> *1, not 0, as the cachemodel size is also the c_block read chunk size, and 0
> never makes progress*

That is exactly right, and 1 is still inside the range where it goes wrong. The
cachemodel size being the read chunk size means a chunk of 1 sector leaves
paranoia's verification logic **no overlap between chunks to compare**, so it
emits zeroes rather than the sectors it read — and because nothing failed to
*read*, the error count stays 0.

### Reproduction

Any BIN/CUE image will do. With a 2-track synthetic image whose `.bin` is the
ground truth:

```sh
cyanrip -d image.cue -N -A -Q -s 0 -o pcm -D out -F '{track}'
cat out/1.pcm out/2.pcm | cmp - image.bin      # differs
cyanrip -d image.cue -N -A -Q -s 0 -o pcm -P 0 -D out0 -F '{track}'
cat out0/1.pcm out0/2.pcm | cmp - image.bin    # identical
```

`-o pcm` writes raw little-endian 16-bit stereo, so for an image with no
pregaps the tracks concatenated are the `.bin` byte for byte.

Sweeping the constant and comparing the decoded PCM against the source `.bin`
directly — not against another cyanrip build:

| `cachemodel_size` | matches source | non-zero samples | `Ripping errors:` |
|---|---|---|---|
| **1** (current) | **no** | **0.3 %** | **0** |
| **4** | **no** | 94.5 % | **0** |
| 5 | yes | 99.2 % | 0 |
| 16 | yes | 99.2 % | 0 |
| 512 | yes | — | 1 |
| 1200 (default) | yes | — | 2 |

Two things worth drawing out:

- **`Ripping errors: 0` throughout the corrupting range.** The failure is
  silent. A user has no signal that anything is wrong, which is what makes this
  worth fixing rather than documenting.
- **4 is corrupt too, and far less obviously.** At 1 the output is 99.7 %
  silence and unmistakable; at 4 it is 94.5 % non-zero and still does not match
  the source. Anyone testing a fix by ear, or by "is it mostly not silence",
  will pass a broken value.

The upper end is bounded by the original problem the commit fixed: at 512 and
above, the backseek probe over-reads the leadout and that gets counted as a read
error. So the workable window is roughly 5–256 for this image, and the upper
bound scales with the image's length.

### Suggested fix

One integer:

```c
cdio_paranoia_cachemodel_size(ctx->paranoia, 16);
```

16 sits an order of magnitude clear of the corruption boundary and an order of
magnitude below where over-reading the leadout starts costing errors. The margin
below the upper bound matters more than the exact figure, since that bound moves
with image size.

### Notes

- Affects `0.9.4-rc1` and anything after `c431d58`, including `0.9.4-rc2` and
  `master` at `f8ebf48`, measured there on 2026-09-27.
- Real drives were never affected; the guard is on the image drivers only.
- `-P 0` is byte-perfect on both, so a consumer pinned to `-P 0` sees nothing.
- Found and fixed downstream in `rmccann-hub/cyanrip` (`platterpus-fork`), where
  the same table is recorded in a comment beside the constant. Happy to open a
  PR if the value is agreed — the reason it is not attached here is that the
  right number is a judgement about the margin, not a mechanical change.
