import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pixelfit.imageops import Image  # noqa: E402
from pixelfit.pngio import read_png, write_png  # noqa: E402


class TestPngRoundtrip(unittest.TestCase):
    def test_roundtrip_all_channel_counts(self):
        for c, color in ((1, (77,)), (3, (12, 200, 90)), (4, (255, 0, 128, 200))):
            img = Image(23, 7, c)
            for y in range(7):
                for x in range(23):
                    i = (y * 23 + x) * c
                    img.data[i:i + c] = bytes(color * c if c == 1 else color)
            path = "/tmp/pf_roundtrip.png"
            img.save(path)
            w, h, cc, data = read_png(path)
            self.assertEqual((w, h, cc), (23, 7, c))
            self.assertEqual(bytes(data), bytes(img.data))

    def test_rejects_unsupported(self):
        # A 16-bit PNG IHDR (depth=16) must be rejected, not misread.
        path = "/tmp/pf_bad.png"
        import struct
        import zlib
        sig = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">IIBBBBB", 4, 4, 16, 2, 0, 0, 0)

        def chunk(t, p):
            return struct.pack(">I", len(p)) + t + p + struct.pack(
                ">I", zlib.crc32(t + p))
        with open(path, "wb") as fh:
            fh.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IEND", b""))
        with self.assertRaises(ValueError):
            read_png(path)


if __name__ == "__main__":
    unittest.main()
