"""Difference hash (dHash) for fast library candidate pruning.

Reduces an image to a 64-bit fingerprint: resample to 9x8 grayscale and
compare adjacent columns. Coarse by design - it distinguishes different
screens, not sibling states of the same screen. The full comparator
does the fine work.
"""
from .imageops import Image, gray_map, resample


def dhash(img):
    """Return a 64-bit fingerprint (int)."""
    small = resample(img, 9, 8)
    gray = gray_map(small)
    bits = 0
    for y in range(8):
        row = y * 9
        for x in range(8):
            bits = (bits << 1) | (1 if gray[row + x] > gray[row + x + 1]
                                  else 0)
    return bits


def hamming(a, b):
    """Bit distance between two fingerprints, 0..64."""
    return bin(a ^ b).count("1")


def fingerprint(path):
    return dhash(Image.load(path))
