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

    # identify which known screen state a screenshot shows
    python3 -m pixelfit match screenshot.png --library my-library

Outputs in `my-report/`:

- `report.md` - human-readable verdict: score, metrics, drifted regions
- `report.json` - the same data, machine-readable
- `diff.png` - the implementation image with red boxes on drifted regions

`match` writes `match.json` and returns exit code 2 when the screenshot
matches no library entry above the floor (unknown state).

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

## Design library (screen states)

A screen rarely has one design: it has a state space (success, empty,
error-by-cause, ...). A library is a directory with `library.json` and
the design PNGs it references:

    {
      "entries": [
        {"key": "home.success",       "image": "home.success.png"},
        {"key": "home.network-error", "image": "home.network-error.png",
         "tags": ["error", "offline"],
         "ignore": [[0, 0, 360, 34]]}
      ]
    }

`pixelfit match screenshot.png --library LIB` identifies which state the
screenshot shows: a 64-bit difference hash prunes the candidates, the
full comparator scores the top few, and the report gives the best match,
the margin over the runner-up, and an unknown-state verdict (exit code
2) when nothing clears the floor (`--floor`, default 90). A small drift
does not break identification; it just shows in the score.

## Ignore regions

`--ignore X0,Y0,X1,Y1` (repeatable, design-pixel coordinates) excludes
rectangles from every metric and from region detection: status bars,
clocks, toasts, ad slots. Library entries can carry their own ignore
rects. Pixels inside ignore rects are excluded, not blanked: the score
is computed over the remaining pixels.

## Profiles and knobs

- `--profile digital|paper` - metric weighting for the design source
- `--threshold 0.1` - per-pixel color sensitivity, 0..1 (0.1 is the
  ecosystem-standard default; 1.0 means only black-vs-white counts)
- `--ignore` - exclusion rects (see above)
- `--floor 90` (match only) - minimum score for a confident match

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
- Automation harness: drive an app with an external UI-automation tool
  (for example Maestro flows on Android), screenshot each step, match
  each step against the library automatically
- Web capture lane: headless-Chromium screenshots with per-element
  boxes and computed styles in one session
- Android capture lane: `adb` screenshots plus view-hierarchy dumps
  (element-level attribution)
- Design-JSON lane: compare a design file's declared values (spacing,
  sizes) against the implementation's declared values
- Batch mode and CI exit-code matrix
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
