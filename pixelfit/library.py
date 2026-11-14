"""Design library: screen-state dictionary + best-match lookup.

A library is a directory with `library.json` and the design PNGs it
references. Each entry is one EXPECTED screen state (success, empty,
error-by-cause, ...). `match` finds which entry a screenshot actually
shows: dHash prunes the candidates, the full comparator scores the top
few, and the report gives best match, margin over the runner-up, and an
unknown-state verdict when nothing scores above the floor.
"""
import json
import os

from . import phash
from .core import compare_images
from .imageops import Image

PRUNE_TOP_K = 3


def load(library_dir):
    """Load a library: list of entry dicts with absolute image paths."""
    path = os.path.join(library_dir, "library.json")
    with open(path) as fh:
        manifest = json.load(fh)
    entries = []
    for e in manifest["entries"]:
        img = os.path.join(library_dir, e["image"])
        entries.append({
            "key": e["key"],
            "image": img,
            "ignore": e.get("ignore", []),
            "tags": e.get("tags", []),
            "_fp": phash.dhash(Image.load(img)),
        })
    if not entries:
        raise ValueError(f"{path}: library has no entries")
    return entries


def match(screenshot_path, library_dir, profile="digital",
          threshold=0.1, floor=90.0, extra_ignore=None):
    """Identify which library entry the screenshot shows.

    Returns a dict: best (key or None), score, margin, unknown flag,
    and the full ranking. `floor` is the minimum fidelity score for a
    confident identification (calibrated; see README).
    """
    entries = load(library_dir)
    shot_fp = phash.dhash(Image.load(screenshot_path))
    shot = Image.load(screenshot_path)
    extra_ignore = extra_ignore or []

    pruned = sorted(entries, key=lambda e: phash.hamming(e["_fp"], shot_fp))
    candidates = pruned[:PRUNE_TOP_K]

    ranking = []
    for e in candidates:
        res = compare_images(Image.load(e["image"]), shot, profile,
                             threshold, e["ignore"] + extra_ignore)
        ranking.append({"key": e["key"], "score": res["fidelity_score"],
                        "result": res})
    ranking.sort(key=lambda r: -r["score"])

    best = ranking[0]
    second = ranking[1]["score"] if len(ranking) > 1 else 0.0
    unknown = best["score"] < floor
    return {
        "screenshot": screenshot_path,
        "profile": profile,
        "best": None if unknown else best["key"],
        "score": best["score"],
        "margin": round(best["score"] - second, 2),
        "unknown": unknown,
        "floor": floor,
        "ranking": [{"key": r["key"], "score": r["score"]}
                    for r in ranking],
    }
