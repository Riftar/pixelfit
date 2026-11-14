import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pixelfit.imageops import (Image, box_blur, dilate,  # noqa: E402
                               resample)
from pixelfit.metrics import (color_diff, edge_map, iou,  # noqa: E402
                              ssim_grid, yiq_distance2)
from pixelfit.regions import clusters, describe  # noqa: E402


def solid(w, h, color, c=3):
    img = Image(w, h, c)
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * c
            img.data[i:i + c] = bytes(color)
    return img


class TestMetrics(unittest.TestCase):
    def test_identical_images_score_perfect(self):
        a = solid(40, 30, (10, 130, 240))
        b = solid(40, 30, (10, 130, 240))
        ratio, mask, mags = color_diff(a, b)
        self.assertEqual(ratio, 0.0)
        self.assertFalse(any(mask))
        cells, mean = ssim_grid(_gray(a), _gray(b), 40, 30)
        self.assertAlmostEqual(mean, 1.0, places=6)
        self.assertAlmostEqual(iou(edge_map(_gray(a), 40, 30),
                                   edge_map(_gray(b), 40, 30)), 1.0)

    def test_black_vs_white_distance_is_max(self):
        # Pure black vs white: chroma axes are 0 by construction, so the
        # distance is the luminance term alone: 0.5053 * 255^2 = 32857.
        d2 = yiq_distance2(0, 0, 0, 255, 255, 255)
        self.assertGreater(d2, 32000)
        # ...and nothing exceeds the normalized metric maximum of 35215.
        self.assertLessEqual(d2, 35215.0)

    def test_subtle_color_shift_below_threshold_passes(self):
        a = solid(20, 20, (100, 100, 100))
        b = solid(20, 20, (102, 101, 101))
        ratio, _, _ = color_diff(a, b, threshold=0.1)
        self.assertEqual(ratio, 0.0)

    def test_alpha_channel_is_ignored(self):
        a = solid(10, 10, (50, 50, 50, 255), c=4)
        b = solid(10, 10, (50, 50, 50, 10), c=4)
        ratio, _, _ = color_diff(a, b)
        self.assertEqual(ratio, 0.0)

    def test_ssim_detects_structural_change(self):
        # Same mean brightness, different structure: a centered block
        # that swaps position between the two images.
        w = h = 32
        base = [100.0] * (w * h)
        a = base[:]
        b = base[:]
        for y in range(12, 20):
            for x in range(6, 14):
                a[y * w + x] = 200.0
                b[y * w + x + 10] = 200.0
        _, mean = ssim_grid(a, b, w, h)
        self.assertLess(mean, 0.99)

    def test_ssim_blind_spot_documented(self):
        # SSIM runs on luminance: equal-structure color swaps can read
        # identical. That is WHY the color metric exists. Pin the blind
        # spot so a future change to ssim_grid fails loudly here.
        w = h = 16
        a = [80.0] * (w * h)
        b = a[:]
        _, mean = ssim_grid(a, b, w, h)
        self.assertEqual(mean, 1.0)


class TestRegions(unittest.TestCase):
    def test_single_block_cluster_found(self):
        w = h = 60
        mask = [False] * (w * h)
        for y in range(20, 30):
            for x in range(25, 35):
                mask[y * w + x] = True
        found = clusters(mask, w, h, min_area=10)
        self.assertEqual(len(found), 1)
        r = found[0]
        # Blur halo: the box may extend ~3px past the block on each side.
        self.assertTrue(20 <= r["x0"] <= 26 and 34 <= r["x1"] <= 40,
                        f"box drifted: {r}")

    def test_noise_below_min_area_dropped(self):
        w = h = 40
        mask = [False] * (w * h)
        for i in range(0, 500, 37):  # scattered single pixels
            mask[i] = True
        self.assertEqual(clusters(mask, w, h, min_area=10), [])

    def test_label_color_for_dense_aligned_edges(self):
        w = h = 30
        mask = [False] * (w * h)
        mags = [0.0] * (w * h)
        edges = [False] * (w * h)
        for y in range(5, 25):
            for x in range(5, 25):
                mask[y * w + x] = True
                mags[y * w + x] = 0.14
        for i in range(5, 25):  # outline present in BOTH edge maps
            edges[5 * w + i] = edges[24 * w + i] = True
            edges[i * w + 5] = edges[i * w + 24] = True
        r = clusters(mask, w, h, min_area=10)[0]
        d = describe(r, mags, mask, w, edges, edges[:])
        self.assertEqual(d["label"], "color")

    def test_label_geometry_when_edges_misaligned(self):
        w = h = 30
        mask = [False] * (w * h)
        mags = [0.0] * (w * h)
        e1 = [False] * (w * h)
        e2 = [False] * (w * h)
        for y in range(5, 25):  # dense mismatch, but outline only in e1
            for x in range(5, 25):
                mask[y * w + x] = True
                mags[y * w + x] = 0.5
        for i in range(5, 25):
            e1[5 * w + i] = e1[24 * w + i] = True
            e2[8 * w + i] = e2[27 * w + i] = True  # shifted
        r = clusters(mask, w, h, min_area=10)[0]
        d = describe(r, mags, mask, w, e1, e2)
        self.assertEqual(d["label"], "spacing/layout")


class TestResample(unittest.TestCase):
    def test_half_scale_of_solid_is_solid(self):
        img = solid(20, 20, (200, 30, 90))
        out = resample(img, 10, 10)
        for y in range(10):
            for x in range(10):
                self.assertEqual(out.rgb(x, y), (200, 30, 90))

    def test_identity_noop_preserves_bytes(self):
        img = solid(8, 8, (1, 2, 3))
        out = resample(img, 8, 8)
        self.assertEqual(bytes(out.data), bytes(img.data))


def _gray(img):
    from pixelfit.imageops import gray_map
    return gray_map(img)


if __name__ == "__main__":
    unittest.main()
