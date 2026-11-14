"""Compare pipeline: two images in, verdict out."""
from . import imageops, metrics, regions
from .imageops import Image

# Profile weights: color / SSIM / edge. `paper` de-weights color because a
# pencil sketch has unreliable color but reliable lines.
PROFILES = {
    "digital": (0.45, 0.35, 0.20),
    "paper": (0.05, 0.40, 0.55),
}

GRID_COLS = 12
GRID_ROWS = 8
EDGE_FRACTION = 0.04


def compare(design_path, impl_path, profile="digital", threshold=0.1):
    """Full comparison. Returns a result dict (JSON-safe)."""
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}; "
                         f"expected one of {sorted(PROFILES)}")
    design = Image.load(design_path)
    impl = Image.load(impl_path)
    return compare_images(design, impl, profile, threshold)


def compare_images(design, impl, profile="digital", threshold=0.1):
    wc, ws, we = PROFILES[profile]
    scaled = False
    if (impl.w, impl.h) != (design.w, design.h):
        impl = imageops.resample(impl, design.w, design.h)
        scaled = True
    w, h = design.w, design.h

    ratio, mask, mags = metrics.color_diff(design, impl, threshold)
    g1 = imageops.gray_map(design)
    g2 = imageops.gray_map(impl)
    cells, ssim_mean = metrics.ssim_grid(g1, g2, w, h, GRID_COLS, GRID_ROWS)
    e1 = imageops.dilate(metrics.edge_map(g1, w, h, EDGE_FRACTION), w, h, 1)
    e2 = imageops.dilate(metrics.edge_map(g2, w, h, EDGE_FRACTION), w, h, 1)
    edge_iou = metrics.iou(e1, e2)

    found = regions.clusters(mask, w, h)
    region_list = []
    for r in found:
        d = regions.describe(r, mags, mask, w, e1, e2)
        r.update(d)
        region_list.append(r)

    color_score = 1.0 - ratio
    score = 100.0 * (wc * color_score + ws * ssim_mean + we * edge_iou)
    worst_cells = sorted(range(len(cells)), key=lambda i: cells[i])[:6]
    return {
        "profile": profile,
        "width": w,
        "height": h,
        "impl_was_resampled": scaled,
        "color_threshold": threshold,
        "metrics": {
            "color_mismatch_ratio": round(ratio, 6),
            "ssim_mean": round(ssim_mean, 6),
            "edge_iou": round(edge_iou, 6),
        },
        "fidelity_score": round(score, 2),
        "regions": region_list,
        "ssim_cells": [round(c, 4) for c in cells],
        "worst_cells": worst_cells,
    }
