# PixelFit sample results

Measured on 2026-11-15 using PixelFit v0.2.0, the digital profile, default
threshold 0.1, and the images in this directory. All inputs are 375 × 812 RGB
PNGs. The Android images were captured from an emulator at 160 dpi. Scores are
observations for these specific images, not pass/fail thresholds.

| Screen | Implementation | Fidelity score | Drifted regions |
| --- | --- | ---: | ---: |
| Home | XML | 71.0 / 100 | 27 |
| Home | Compose | 71.4 / 100 | 27 |
| Rewards | XML | 83.6 / 100 | 20 |
| Rewards | Compose | 80.9 / 100 | 20 |

Run the commands in [README.md](README.md) to reproduce the comparisons.
The saved `images/*-diff.png` files show the implementation annotated with
the resulting region boxes. Home and Rewards references were exported after
the Figma text styles were aligned with standard Roboto.

## Observations

- The Rewards render uses the exported referral and share illustrations. Home
  coin logos are placeholders, and both screens have incomplete system and
  bottom-navigation icons. These omissions contribute to the measured drift.
- Text can still be marked even with the same Roboto family. The screenshots
  show position differences and may differ in glyph rasterization and font
  metrics. PixelFit compares pixels; it does not identify font families.
- At the default threshold the Rewards Compose overlay groups both colored
  cards in one rectangle. Only 8% of that rectangle's pixels are mismatched.
  The region clustering blurs and merges nearby mismatches, so the box covers
  the combined region rather than indicating that the entire card differs.
- The `spacing/layout` label is a coarse heuristic and does not identify the
  cause of a particular text or card difference.
- During the original run, annotated output for grayscale and RGBA screenshots
  was found to be invalid in the upstream CLI because the red outline was
  written using three channels. The supplied comparison images are opaque RGB
  PNGs, which avoid that issue. Transparent illustration assets retain alpha.

## Tolerance experiment

Rewards Compose against the same Figma reference with varying `--threshold`:

| Threshold | Color mismatch | Fidelity score | Regions |
| ---: | ---: | ---: | ---: |
| 0.1 | 5.56% | 80.9 / 100 | 20 |
| 0.2 | 4.35% | 81.4 / 100 | 20 |
| 0.3 | 3.37% | 81.9 / 100 | 22 |
| 0.4 | 2.55% | 82.2 / 100 | 23 |

The threshold changes the per-pixel color mask. It does not change the SSIM
or edge IoU metrics; those remained 0.7982 and 0.5221 respectively in this
experiment. Some text remained marked at 0.3 and 0.4. Higher thresholds can
split regions, so fewer mismatched pixels do not necessarily mean fewer boxes.
For example:

```sh
python -m pixelfit samples/android-crypto/images/rewards-figma.png samples/android-crypto/images/rewards-compose.png --threshold 0.3 --out pixelfit-out/rewards-compose-03
```
