# Draft: upstream bug report for cyanreg/cyanrip

**Not filed.** This is a draft for the maintainer to review and submit; filing on
upstream's tracker is outside this repository. Platterpus's ruling (round 7,
H11) was *"yes, and I would not wait"* — if upstream picks a different value we
want to know now rather than at the next rebase.

Everything below was re-derived immediately before writing it, against the source
bytes rather than against another build.

---

## Title

Ripping a disc image at any paranoia level returns corrupted audio and reports `Ripping errors: 0`

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
cyanrip -d image.cue -N -A -Q -s 0 -o wav -D out -F '{track}'
cmp out/1.wav image.bin      # differs
```

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

- Affects `0.9.4-rc1` and anything after `c431d58`.
- Real drives were never affected; the guard is on the image drivers only.
- `-P 0` is byte-perfect on both, so a consumer pinned to `-P 0` sees nothing.
- Found and fixed downstream in `rmccann-hub/cyanrip` (`platterpus-fork`), where
  the same table is recorded in a comment beside the constant. Happy to open a
  PR if the value is agreed — the reason it is not attached here is that the
  right number is a judgement about the margin, not a mechanical change.
