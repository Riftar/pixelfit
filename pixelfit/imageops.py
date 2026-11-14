"""Image container and pure-Python raster operations."""
from . import pngio


class Image:
    """Flat-buffer image: 1 (gray), 3 (RGB) or 4 (RGBA) channels, 8-bit."""

    __slots__ = ("w", "h", "c", "data")

    def __init__(self, w, h, c, data=None):
        self.w, self.h, self.c = w, h, c
        self.data = data if data is not None else bytearray(w * h * c)

    @classmethod
    def load(cls, path):
        w, h, c, data = pngio.read_png(path)
        return cls(w, h, c, data)

    def save(self, path):
        pngio.write_png(path, self.w, self.h, self.c, bytes(self.data))

    def px(self, x, y):
        """Return the pixel as a tuple (r, g, b[, a])."""
        i = (y * self.w + x) * self.c
        d = self.data
        if self.c == 1:
            return (d[i],)
        return tuple(d[i:i + self.c])

    def rgb(self, x, y):
        """Return (r, g, b), dropping alpha (treated as opaque)."""
        p = self.px(x, y)
        if self.c == 1:
            return (p[0], p[0], p[0])
        return p[:3]

    def clone(self):
        return Image(self.w, self.h, self.c, bytearray(self.data))


def resample(img, w, h):
    """Area-average resample to (w, h). Deterministic."""
    if img.w == w and img.h == h:
        return img.clone()
    out = Image(w, h, img.c)
    c = img.c
    sx, sy = img.w / w, img.h / h
    src, dst = img.data, out.data
    for ty in range(h):
        y0, y1 = ty * sy, (ty + 1) * sy
        iy0, iy1 = int(y0), int(y1)
        if iy1 - iy0 < 1:
            iy1 = iy0 + 1
        for tx in range(w):
            x0, x1 = tx * sx, (tx + 1) * sx
            ix0, ix1 = int(x0), int(x1)
            if ix1 - ix0 < 1:
                ix1 = ix0 + 1
            acc = [0] * c
            area = 0.0
            for yy in range(iy0, min(iy1, img.h)):
                wy = min(y1, yy + 1) - max(y0, yy)
                if wy <= 0:
                    continue
                row = yy * img.w
                for xx in range(ix0, min(ix1, img.w)):
                    wx = min(x1, xx + 1) - max(x0, xx)
                    if wx <= 0:
                        continue
                    a = wy * wx
                    area += a
                    i = (row + xx) * c
                    for k in range(c):
                        acc[k] += src[i + k] * a
            o = (ty * w + tx) * c
            if area > 0:
                for k in range(c):
                    dst[o + k] = int(acc[k] / area + 0.5)
    return out


def gray_map(img):
    """Luminance as a list of floats, length w*h."""
    w, h, c = img.w, img.h, img.c
    d = img.data
    out = [0.0] * (w * h)
    if c == 1:
        return [float(v) for v in d]
    for i, o in zip(range(0, w * h * c, c), range(w * h)):
        r, g, b = d[i], d[i + 1], d[i + 2]
        out[o] = 0.299 * r + 0.587 * g + 0.114 * b
    return out


def box_blur(vals, w, h, r):
    """Box blur a scalar map (floats) with radius r, edge-clamped."""
    if r <= 0:
        return vals[:]
    tmp = [0.0] * (w * h)
    out = [0.0] * (w * h)
    for y in range(h):
        row = y * w
        x0 = max(0, -r)
        acc = sum(vals[row:row + r + 1])
        cnt = min(r + 1, w)
        for x in range(w):
            tmp[row + x] = acc / cnt
            add = x + r + 1
            sub = x - r
            if add < w:
                acc += vals[row + add]
                cnt += 1
            if sub >= 0:
                acc -= vals[row + sub]
                cnt -= 1
    for x in range(w):
        acc = 0.0
        cnt = 0
        for y in range(0, min(r + 1, h)):
            acc += tmp[y * w + x]
            cnt += 1
        for y in range(h):
            out[y * w + x] = acc / cnt
            add = y + r + 1
            sub = y - r
            if add < h:
                acc += tmp[add * w + x]
                cnt += 1
            if sub >= 0:
                acc -= tmp[sub * w + x]
                cnt -= 1
    return out


def dilate(mask, w, h, r=1):
    """Binary dilation (bool list) with a square structuring element."""
    if r <= 0:
        return mask[:]
    tmp = [False] * (w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            if mask[row + x]:
                for dx in range(-r, r + 1):
                    xx = x + dx
                    if 0 <= xx < w:
                        tmp[row + xx] = True
    out = [False] * (w * h)
    for y in range(h):
        for x in range(w):
            if tmp[y * w + x]:
                for dy in range(-r, r + 1):
                    yy = y + dy
                    if 0 <= yy < h:
                        out[yy * w + x] = True
    return out
