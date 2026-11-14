"""CLI: compare a design image against an implementation screenshot."""
import argparse
import json
import os
import sys

from . import core
from .imageops import Image
from .paint import stroke_rect


def _annotated(impl_norm, region_list):
    out = impl_norm.clone()
    for r in region_list:
        stroke_rect(out, r["x0"], r["y0"], r["x1"] - r["x0"],
                    r["y1"] - r["y0"], (255, 0, 0), 2)
    return out


def _markdown(res, design_path, impl_path):
    lines = [
        "# pixelfit report",
        "",
        f"- design: `{design_path}`",
        f"- implementation: `{impl_path}`",
        f"- canvas: {res['width']}x{res['height']}"
        + (" (implementation resampled)" if res["impl_was_resampled"] else ""),
        f"- profile: {res['profile']}",
        "",
        f"## Fidelity score: {res['fidelity_score']:.1f} / 100",
        "",
        f"- color mismatch: {res['metrics']['color_mismatch_ratio'] * 100:.2f}%"
        " of pixels",
        f"- structure (SSIM): {res['metrics']['ssim_mean']:.4f}",
        f"- layout skeleton (edge IoU): {res['metrics']['edge_iou']:.4f}",
        "",
    ]
    if res["regions"]:
        lines.append(f"## Drifted regions ({len(res['regions'])})")
        lines.append("")
        for i, r in enumerate(res["regions"], 1):
            lines.append(
                f"- **#{i}** [{r['label']}] box=({r['x0']},{r['y0']})-"
                f"({r['x1']},{r['y1']}) severity={r['mean_magnitude']:.2f} "
                f"fill={r['fill']:.0%}")
    else:
        lines.append("No drifted regions detected.")
    lines.append("")
    lines.append("Diff overlay: `diff.png` (red boxes = drifted regions).")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="pixelfit",
        description="Measure how closely an implementation screenshot "
                    "matches a design image. Zero dependencies, offline.")
    ap.add_argument("design", help="design image PNG (Figma/Canva export, "
                                   "sketch photo, any 8-bit non-interlaced PNG)")
    ap.add_argument("impl", help="implementation screenshot PNG "
                                 "(web or mobile)")
    ap.add_argument("--profile", choices=sorted(core.PROFILES),
                    default="digital",
                    help="input profile: digital (default) or paper "
                         "(sketch photos; edge-weighted)")
    ap.add_argument("--threshold", type=float, default=0.1,
                    help="per-pixel color threshold, 0..1 (default 0.1)")
    ap.add_argument("--out", default="pixelfit-out", metavar="DIR",
                    help="output directory (default pixelfit-out)")
    args = ap.parse_args(argv)

    res = core.compare(args.design, args.impl, args.profile, args.threshold)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "report.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    with open(os.path.join(args.out, "report.md"), "w") as fh:
        fh.write(_markdown(res, args.design, args.impl))
    impl = Image.load(args.impl)
    if (impl.w, impl.h) != (res["width"], res["height"]):
        from .imageops import resample
        impl = resample(impl, res["width"], res["height"])
    _annotated(impl, res["regions"]).save(os.path.join(args.out, "diff.png"))

    print(f"fidelity score: {res['fidelity_score']:.1f}/100 "
          f"({res['profile']} profile, {len(res['regions'])} drifted "
          f"region(s))")
    print(f"report: {args.out}/report.md  diff overlay: {args.out}/diff.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
