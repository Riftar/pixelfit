"""Library-match and ignore-region gates."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pixelfit import phash  # noqa: E402
from pixelfit.core import compare  # noqa: E402
from pixelfit.imageops import Image  # noqa: E402
from pixelfit.library import load, match  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(HERE), "fixtures", "library")


class TestLibraryMatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(LIB, "library.json")):
            pass  # existence check; load() parses below
        cls.entries = load(LIB)

    def test_library_loads_with_fingerprints(self):
        keys = sorted(e["key"] for e in self.entries)
        self.assertEqual(keys, ["home.empty", "home.network-error",
                                "home.success"])
        self.assertTrue(all("_fp" in e for e in self.entries))

    def test_success_screenshot_matches_success(self):
        res = match(os.path.join(LIB, "impl-state-success.png"), LIB)
        self.assertEqual(res["best"], "home.success")
        self.assertFalse(res["unknown"])
        self.assertGreaterEqual(res["score"], 99.0)

    def test_drifted_error_screenshot_still_matches_error(self):
        res = match(os.path.join(LIB, "impl-state-error.png"), LIB)
        self.assertEqual(res["best"], "home.network-error")
        self.assertLess(res["score"], 100.0)  # drift is visible in score

    def test_unknown_screen_is_flagged(self):
        res = match(os.path.join(LIB, "impl-state-unknown.png"), LIB)
        self.assertTrue(res["unknown"])
        self.assertIsNone(res["best"])

    def test_dhash_separates_unrelated_screens(self):
        a = phash.dhash(Image.load(os.path.join(LIB, "home.success.png")))
        b = phash.dhash(Image.load(
            os.path.join(LIB, "impl-state-unknown.png")))
        self.assertGreater(phash.hamming(a, b), 10)
        same = phash.dhash(Image.load(
            os.path.join(LIB, "impl-state-success.png")))
        self.assertEqual(phash.hamming(a, same), 0)


class TestIgnoreRegions(unittest.TestCase):
    """Clock-region drift: invisible with the ignore rect, caught without."""

    @classmethod
    def setUpClass(cls):
        design = Image(200, 120, 3)
        from pixelfit.paint import fill_rect
        for y in range(120):
            for x in range(200):
                i = (y * 200 + x) * 3
                design.data[i:i + 3] = bytes((240, 240, 244))
        fill_rect(design, 10, 10, 120, 20, (30, 40, 50))
        fill_rect(design, 160, 10, 30, 8, (200, 30, 30))  # the "clock"
        impl = design.clone()
        fill_rect(impl, 160, 10, 30, 8, (240, 240, 244))  # clock gone
        design.save("/tmp/pf_ign_design.png")
        impl.save("/tmp/pf_ign_impl.png")
        cls.design = "/tmp/pf_ign_design.png"
        cls.impl = "/tmp/pf_ign_impl.png"
        cls.rect = [[155, 5, 195, 25]]

    def test_without_ignore_clock_is_caught(self):
        res = compare(self.design, self.impl)
        self.assertLess(res["fidelity_score"], 99.0)
        self.assertTrue(res["regions"])

    def test_with_ignore_clock_is_invisible(self):
        res = compare(self.design, self.impl, ignore=self.rect)
        self.assertGreaterEqual(res["fidelity_score"], 99.9)
        self.assertEqual(res["regions"], [])


if __name__ == "__main__":
    unittest.main()
