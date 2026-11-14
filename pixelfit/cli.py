"""CLI: compare a design image against an implementation screenshot,
or identify which library state a screenshot shows."""
import argparse
import json
import os
import sys

from . import core, library
from .imageops import Image, resample
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


def _parse_rects(values):
    rects = []
    for v in values or []:
        parts = [int(p) for p in v.split(",")]
        if len(parts) != 4:
            raise SystemExit(f"--ignore expects x0,y0,x1,y1, got {v!r}")
        rects.append(parts)
    return rects


def _run_compare(args):
    res = core.compare(args.design, args.impl, args.profile,
                       args.threshold, _parse_rects(args.ignore))
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "report.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    with open(os.path.join(args.out, "report.md"), "w") as fh:
        fh.write(_markdown(res, args.design, args.impl))
    impl = Image.load(args.impl)
    if (impl.w, impl.h) != (res["width"], res["height"]):
        impl = resample(impl, res["width"], res["height"])
    _annotated(impl, res["regions"]).save(os.path.join(args.out, "diff.png"))
    print(f"fidelity score: {res['fidelity_score']:.1f}/100 "
          f"({res['profile']} profile, {len(res['regions'])} drifted "
          f"region(s))")
    print(f"report: {args.out}/report.md  diff overlay: {args.out}/diff.png")
    return 0


def _run_match(args):
    res = library.match(args.screenshot, args.library, args.profile,
                        args.threshold, args.floor,
                        _parse_rects(args.ignore))
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "match.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    top_key = (res["best"] or res["ranking"][0]["key"])
    if res["unknown"]:
        print(f"UNKNOWN STATE: no library entry scores >= {res['floor']} "
              f"(closest: {top_key} at {res['score']:.1f})")
        ret = 2
    else:
        print(f"matched: {res['best']} "
              f"(score {res['score']:.1f}, margin {res['margin']:.1f})")
        ret = 0
    for r in res["ranking"]:
        print(f"  {r['key']:24} {r['score']:6.1f}")
    print(f"report: {args.out}/match.json")
    return ret


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # Backward compatibility: bare "design impl" still means compare.
    if argv and argv[0] not in ("compare", "match", "-h", "--help"):
        argv.insert(0, "compare")

    ap = argparse.ArgumentParser(
        prog="pixelfit",
        description="Measure how closely an implementation screenshot "
                    "matches a design image, or identify which known "
                    "screen state a screenshot shows. Zero dependencies, "
                    "offline.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--profile", choices=sorted(core.PROFILES),
                       default="digital",
                       help="input profile: digital (default) or paper "
                            "(sketch photos; edge-weighted)")
        p.add_argument("--threshold", type=float, default=0.1,
                       help="per-pixel color threshold, 0..1 (default 0.1)")
        p.add_argument("--ignore", action="append", metavar="X0,Y0,X1,Y1",
                       help="rect excluded from all metrics (repeatable)")
        p.add_argument("--out", default="pixelfit-out", metavar="DIR",
                       help="output directory (default pixelfit-out)")

    pc = sub.add_parser("compare", help="compare design vs screenshot")
    pc.add_argument("design", help="design image PNG (Figma/Canva export, "
                                   "sketch photo, plain PNG)")
    pc.add_argument("impl", help="implementation screenshot PNG "
                                 "(web or mobile)")
    common(pc)
    pc.set_defaults(func=_run_compare)

    pm = sub.add_parser("match", help="identify which library state a "
                                      "screenshot shows")
    pm.add_argument("screenshot", help="implementation screenshot PNG")
    pm.add_argument("--library", required=True, metavar="DIR",
                    help="library directory (contains library.json)")
    pm.add_argument("--floor", type=float, default=90.0,
                    help="minimum score for a confident match (default 90)")
    common(pm)
    pm.set_defaults(func=_run_match)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
