"""Comparison metrics: perceptual color diff, SSIM grid, edge-map IoU.

All pure Python over flat scalar maps. Calibrated conventions follow the
widely-deployed comparator lineage: YIQ weighted color distance with a
0..1 threshold scale against a black/white maximum of 35215, SSIM over
grid cells with C1/C2 stabilizers at 255 dynamic range.
"""

# YIQ channel weights for squared distance (perceptual, luminance-heavy).
_W_Y, _W_I, _W_Q = 0.5053, 0.299, 0.1957
_MAXYIQ = 35215.0  # metric value of black-vs-white
_C1 = (0.01 * 255) ** 2
_C2 = (0.03 * 255) ** 2


def yiq_distance2(r1, g1, b1, r2, g2, b2):
    """Squared perceptual color distance between two RGB pixels."""
    y1 = 0.299 * r1 + 0.587 * g1 + 0.114 * b1
    i1 = 0.596 * r1 - 0.274 * g1 - 0.322 * b1
    q1 = 0.211 * r1 - 0.523 * g1 + 0.312 * b1
    y2 = 0.299 * r2 + 0.587 * g2 + 0.114 * b2
    i2 = 0.596 * r2 - 0.274 * g2 - 0.322 * b2
    q2 = 0.211 * r2 - 0.523 * g2 + 0.312 * b2
    return _W_Y * (y1 - y2) ** 2 + _W_I * (i1 - i2) ** 2 + _W_Q * (q1 - q2) ** 2


def color_diff(a, b, threshold=0.1):
    """Per-pixel perceptual comparison of two same-size images.

    Alpha channels are ignored (pixels treated as opaque).
    Returns (mismatch_ratio, mismatch_mask, magnitude_map):
    - mismatch_mask: bool per pixel
    - magnitude_map: normalized 0..1 distance (1 = black-vs-white)
    """
    if (a.w, a.h) != (b.w, b.h):
        raise ValueError("color_diff requires equal-size images")
    if a.c != 3:
        a = _as_rgb(a)
    if b.c != 3:
        b = _as_rgb(b)
    w, h = a.w, a.h
    n = w * h
    da, db = a.data, b.data
    limit = _MAXYIQ * threshold * threshold
    mask = [False] * n
    mags = [0.0] * n
    mismatched = 0
    for o in range(n):
        i = o * 3
        d2 = yiq_distance2(da[i], da[i + 1], da[i + 2],
                           db[i], db[i + 1], db[i + 2])
        if d2 > limit:
            mask[o] = True
            mismatched += 1
            mags[o] = min(1.0, (d2 / _MAXYIQ) ** 0.5)
    return mismatched / n, mask, mags


def _as_rgb(img):
    from .imageops import Image
    if img.c == 3:
        return img
    out = Image(img.w, img.h, 3)
    for y in range(img.h):
        for x in range(img.w):
            r, g, b = img.rgb(x, y)
            i = (y * img.w + x) * 3
            out.data[i:i + 3] = bytes((int(r), int(g), int(b)))
    return out


def _integral(vals, w, h):
    """2D integral image, (h+1) x (w+1) row-major."""
    intg = [0.0] * ((w + 1) * (h + 1))
    width1 = w + 1
    for y in range(h):
        row_sum = 0.0
        base = y * width1
        nxt = (y + 1) * width1
        for x in range(w):
            row_sum += vals[y * w + x]
            intg[nxt + x + 1] = intg[base + x + 1] + row_sum
    return intg


def _rect_sum(intg, w, x0, y0, x1, y1):
    """Sum over [x0,x1) x [y0,y1) from an integral image."""
    width1 = w + 1
    return (intg[y1 * width1 + x1] - intg[y0 * width1 + x1]
            - intg[y1 * width1 + x0] + intg[y0 * width1 + x0])


def ssim_grid(g1, g2, w, h, cols=12, rows=8):
    """Per-cell SSIM over a cols x rows grid.

    Returns (cells, mean): cells is row-major list of cols*rows scores,
    mean is their area-weighted mean. Each cell's SSIM is computed from
    the cell's aggregate statistics (mean/variance/covariance), which is
    the standard fast approximation of windowed SSIM.
    """
    n = w * h
    i1 = _integral(g1, w, h)
    i2 = _integral(g2, w, h)
    sq1 = _integral([v * v for v in g1], w, h)
    sq2 = _integral([v * v for v in g2], w, h)
    cr = _integral([a * b for a, b in zip(g1, g2)], w, h)
    cells = []
    total, total_area = 0.0, 0
    for gy in range(rows):
        y0 = gy * h // rows
        y1 = (gy + 1) * h // rows
        if y1 <= y0:
            y1 = min(h, y0 + 1)
        for gx in range(cols):
            x0 = gx * w // cols
            x1 = (gx + 1) * w // cols
            if x1 <= x0:
                x1 = min(w, x0 + 1)
            area = (x1 - x0) * (y1 - y0)
            if area == 0:
                cells.append(1.0)
                continue
            s1 = _rect_sum(i1, w, x0, y0, x1, y1)
            s2 = _rect_sum(i2, w, x0, y0, x1, y1)
            v1 = _rect_sum(sq1, w, x0, y0, x1, y1)
            v2 = _rect_sum(sq2, w, x0, y0, x1, y1)
            cv = _rect_sum(cr, w, x0, y0, x1, y1)
            mu1, mu2 = s1 / area, s2 / area
            var1 = max(0.0, v1 / area - mu1 * mu1)
            var2 = max(0.0, v2 / area - mu2 * mu2)
            cov = cv / area - mu1 * mu2
            score = ((2 * mu1 * mu2 + _C1) * (2 * cov + _C2)) / (
                (mu1 * mu1 + mu2 * mu2 + _C1) * (var1 + var2 + _C2))
            cells.append(max(-1.0, min(1.0, score)))
            total += score * area
            total_area += area
    mean = total / total_area if total_area else 1.0
    return cells, mean


def sobel_magnitude(gray, w, h):
    """Gradient magnitude (list of floats), borders zeroed."""
    out = [0.0] * (w * h)
    for y in range(1, h - 1):
        row = y * w
        for x in range(1, w - 1):
            i = row + x
            tl = gray[i - w - 1]
            t = gray[i - w]
            tr = gray[i - w + 1]
            l = gray[i - 1]
            r = gray[i + 1]
            bl = gray[i + w - 1]
            btm = gray[i + w]
            br = gray[i + w + 1]
            gx = (tr + 2 * r + br) - (tl + 2 * l + bl)
            gy = (bl + 2 * btm + br) - (tl + 2 * t + tr)
            out[i] = (gx * gx + gy * gy) ** 0.5
    return out


def edge_map(gray, w, h, frac=0.04):
    """Binary edge map: top `frac` of ALL pixels by gradient magnitude.

    The budget is relative to w*h (not to nonzero gradients): flat-color
    UI screenshots have few live gradients, and a live-relative budget
    degenerates to a handful of pixels that ignore whole-element shifts.
    """
    n = w * h
    mags = sobel_magnitude(gray, w, h)
    live = sorted(m for m in mags if m > 2.0)
    keep = max(1, int(n * frac))
    if not live:
        return [False] * n
    if keep >= len(live):
        thresh = 2.0
    else:
        thresh = live[len(live) - keep]
    return [m > thresh for m in mags]


def iou(mask_a, mask_b):
    """Intersection-over-union of two bool masks."""
    inter = union = 0
    for a, b in zip(mask_a, mask_b):
        if a or b:
            union += 1
            if a and b:
                inter += 1
    return inter / union if union else 1.0
