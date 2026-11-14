"""End-to-end gates on the fixture corpus.

The fixture generator records ground truth (which region drifted, how).
Tests assert: clean pair is perfect; every drifted variant is caught by
at least one region overlapping the ground-truth box; the color variant
reports a color-labeled region; the missing-card variant tanks SSIM.
Thresholds were MEASURED on these fixtures, then set slightly under.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pixelfit.core import compare  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(os.path.dirname(HERE), "fixtures")


def _result(variant, profile="digital"):
    return compare(os.path.join(FIX, "design.png"),
                   os.path.join(FIX, f"impl-{variant}.png"), profile)


def _overlap(a, b):
    ix = max(0, min(a["x1"], b[2]) - max(a["x0"], b[0]))
    iy = max(0, min(a["y1"], b[3]) - max(a["y0"], b[1]))
    return ix * iy


class TestEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(FIX, "manifest.json")) as fh:
            cls.manifest = json.load(fh)

    def test_clean_pair_is_near_perfect(self):
        res = _result("clean")
        self.assertGreaterEqual(res["fidelity_score"], 99.9)
        self.assertEqual(res["regions"], [])
        self.assertAlmostEqual(res["metrics"]["ssim_mean"], 1.0, places=4)
        self.assertAlmostEqual(res["metrics"]["edge_iou"], 1.0, places=4)

    def test_every_drift_variant_is_caught(self):
        for variant, gt in self.manifest["ground_truth"].items():
            with self.subTest(variant=variant):
                res = _result(variant)
                hits = [r for r in res["regions"] if _overlap(r, gt) > 0]
                self.assertTrue(hits, f"{variant}: no region overlaps GT")
                self.assertLess(res["fidelity_score"], 99.0)

    def test_recolor_reports_color_label(self):
        res = _result("recolor_card")
        color_regions = [r for r in res["regions"] if r["label"] == "color"]
        self.assertTrue(color_regions, "recolor variant not labeled color")

    def test_missing_card_tanks_ssim(self):
        clean = _result("clean")
        missing = _result("missing_card")
        self.assertLess(missing["metrics"]["ssim_mean"],
                        clean["metrics"]["ssim_mean"] - 0.01)

    def test_geometry_variants_lower_edge_iou(self):
        clean = _result("clean")
        for variant in ("shift_button", "spacing", "wide_button"):
            with self.subTest(variant=variant):
                res = _result(variant)
                self.assertLess(res["metrics"]["edge_iou"],
                                clean["metrics"]["edge_iou"] - 0.01)

    def test_paper_profile_still_catches_geometry(self):
        res = _result("shift_button", profile="paper")
        gt = self.manifest["ground_truth"]["shift_button"]
        hits = [r for r in res["regions"] if _overlap(r, gt) > 0]
        self.assertTrue(hits)


if __name__ == "__main__":
    unittest.main()
