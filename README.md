# pixelfit

Measure how closely a built UI matches its design. Two images in: a
fidelity score, a per-region breakdown of what drifted, and an annotated
diff overlay. Zero dependencies, fully offline, Python stdlib only.

    python3 -m pixelfit design.png screenshot.png --profile digital

Works with any design source that can export an image: Figma frames,
Canva exports, sketch photos, plain PNGs. The implementation side is any
screenshot: web or mobile.

## Quick start

    # run the test suite (fixtures ship in the repo, no setup needed)
    python3 -m unittest discover -s tests

    # compare a design against an implementation screenshot
    python3 -m pixelfit design.png screenshot.png --out my-report

Outputs in `my-report/`:

- `report.md` - human-readable verdict: score, metrics, drifted regions
- `report.json` - the same data, machine-readable
- `diff.png` - the implementation image with red boxes on drifted regions

## How it works

Three independent metrics, because each one is blind to what the others
see:

1. **Perceptual color diff** - per-pixel distance in YIQ space (weighted
   luminance + chroma, the classic comparator lineage). Catches color
   drift. Blind spot: none for color, but it screams on any subpixel
   rendering difference, which is why it is not the only metric.
2. **SSIM grid** - structural similarity per 12x8 grid cell: local
   luminance, contrast, structure. Tolerates rendering noise; catches
   missing or reshaped content. Documented blind spot: it runs on
   luminance, so a pure color swap at equal brightness reads as
   identical (the color metric exists for exactly that).
3. **Edge IoU** - Sobel edge maps from both images, dilated, scored by
   intersection-over-union. This is the layout skeleton: it survives
   completely different fonts or textures as long as the structure
   lines up. It is what makes the `paper` profile possible, since a
   pencil sketch has no reliable color but does have lines.

Drifted regions come from clustering the color-diff mask (blur,
threshold, connected components, gap-merge). Each region is labeled
`color` (dense mismatch, element outline still aligned) or
`spacing/layout` (edges misaligned or partial fill).

The fidelity score is a weighted blend set by the profile:

- `digital` (Figma, Canva, PNG): color 45 / SSIM 35 / edges 20
- `paper` (sketch photos): color 5 / SSIM 40 / edges 55

## Profiles and knobs

- `--profile digital|paper` - metric weighting for the design source
- `--threshold 0.1` - per-pixel color sensitivity, 0..1 (0.1 is the
  ecosystem-standard default; 1.0 means only black-vs-white counts)

## Supported PNG scope

8-bit, non-interlaced, gray / RGB / RGBA. Anything else is rejected
with a clear error rather than misread. Alpha is ignored (pixels are
treated as opaque). If the implementation image has a different size it
is area-averaged to the design's dimensions and the report says so.

## Honest limits (measured on the bundled corpus)

- A uniform shift of a large element produces several mismatch bands
  inside its footprint (one per sub-element boundary), not one box.
  The regions still localize the drift correctly.
- Region labels are a coarse CP1 heuristic: `color` vs `spacing/layout`
  only, no per-CSS-property attribution in this version.
- Scores were calibrated on synthetic fixture pairs with known drift
  (a clean pair scores exactly 100; the fixture drifts score 89-96).
  Recalibrate expectations on your own real pairs: run a pair you know
  is good, note the score, and gate relative to that.
- Pure Python: expect a few seconds per compare at 360x240 and roughly
  linear scaling with pixel count.

## Roadmap (future versions)

- Overlay web viewer: side-by-side, opacity slider, heatmap
- Web capture lane: headless-Chromium screenshots with per-element
  boxes and computed styles in one session
- Android capture lane: `adb` screenshots plus view-hierarchy dumps
  (element-level attribution)
- Design-JSON lane: compare a design file's declared values (spacing,
  sizes) against the implementation's declared values
- Batch mode, ignore regions, CI exit codes
- Deterministic patch suggestions for numeric drift (delivered as git
  patches; never auto-applied)

## Development

    python3 fixtures/gen_fixtures.py   # regenerate fixtures (deterministic)
    python3 -m unittest discover -s tests

The fixture generator renders a synthetic design screen and drifted
implementation twins (shifted button, recolored card, missing card,
changed spacing, resized button) and records ground truth; the
end-to-end tests gate on detection of the known drift.

## License

MIT
