"""Paint helpers: flat-shape rasterization for fixtures and annotations.

No fonts, no anti-aliasing: rectangles, rounded rectangles, circles.
"""
from .imageops import Image


def fill_rect(img, x, y, w, h, color):
    c = img.c
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(img.w, x + w), min(img.h, y + h)
    d = img.data
    for yy in range(y0, y1):
        row = (yy * img.w) * c
        for xx in range(x0, x1):
            i = row + xx * c
            d[i:i + c] = color


def fill_circle(img, cx, cy, r, color):
    c = img.c
    r2 = r * r
    for yy in range(max(0, cy - r), min(img.h, cy + r + 1)):
        dy = yy - cy
        for xx in range(max(0, cx - r), min(img.w, cx + r + 1)):
            dx = xx - cx
            if dx * dx + dy * dy <= r2:
                i = (yy * img.w + xx) * c
                img.data[i:i + c] = color


def fill_rounded_rect(img, x, y, w, h, r, color):
    fill_rect(img, x + r, y, w - 2 * r, h, color)
    fill_rect(img, x, y + r, w, h - 2 * r, color)
    fill_circle(img, x + r, y + r, r, color)
    fill_circle(img, x + w - r - 1, y + r, r, color)
    fill_circle(img, x + r, y + h - r - 1, r, color)
    fill_circle(img, x + w - r - 1, y + h - r - 1, r, color)


def stroke_rect(img, x, y, w, h, color, t=2):
    fill_rect(img, x, y, w, t, color)
    fill_rect(img, x, y + h - t, w, t, color)
    fill_rect(img, x, y, t, h, color)
    fill_rect(img, x + w - t, y, t, h, color)
