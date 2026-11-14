"""Drifted-region clustering: diff mask -> bounding boxes with severity."""
from .imageops import box_blur


def _merge_boxes(boxes, gap):
    """Transitively merge boxes whose gap-expanded rectangles intersect."""
    merged = True
    while merged:
        merged = False
        out = []
        for b in boxes:
            hit = None
            for o in out:
                if (b["x0"] - gap < o["x1"] and o["x0"] - gap < b["x1"]
                        and b["y0"] - gap < o["y1"] and o["y0"] - gap < b["y1"]):
                    hit = o
                    break
            if hit is None:
                out.append(dict(b))
            else:
                hit["x0"] = min(hit["x0"], b["x0"])
                hit["y0"] = min(hit["y0"], b["y0"])
                hit["x1"] = max(hit["x1"], b["x1"])
                hit["y1"] = max(hit["y1"], b["y1"])
                hit["area"] += b["area"]
                merged = True
        boxes = out
    return boxes


def clusters(mask, w, h, min_area=24, blur_radius=3, density=0.08,
             merge_gap=12):
    """Cluster a per-pixel mismatch mask into regions.

    Blurs the mask density so scattered noise merges, thresholds, then
    flood-fills (4-connectivity). Components under min_area are dropped.
    Returns a list of dicts sorted by area (desc):
      {"x0", "y0", "x1", "y1", "area"}  (x1/y1 exclusive)
    """
    density_map = box_blur([1.0 if m else 0.0 for m in mask], w, h,
                           blur_radius)
    hot = [d >= density for d in density_map]
    seen = [False] * (w * h)
    out = []
    for start in range(w * h):
        if not hot[start] or seen[start]:
            continue
        stack = [start]
        seen[start] = True
        x0, y0, x1, y1 = w, h, 0, 0
        area = 0
        while stack:
            i = stack.pop()
            x, y = i % w, i // w
            area += 1
            if x < x0:
                x0 = x
            if x > x1:
                x1 = x
            if y < y0:
                y0 = y
            if y > y1:
                y1 = y
            if x > 0 and hot[i - 1] and not seen[i - 1]:
                seen[i - 1] = True
                stack.append(i - 1)
            if x + 1 < w and hot[i + 1] and not seen[i + 1]:
                seen[i + 1] = True
                stack.append(i + 1)
            if y > 0 and hot[i - w] and not seen[i - w]:
                seen[i - w] = True
                stack.append(i - w)
            if y + 1 < h and hot[i + w] and not seen[i + w]:
                seen[i + w] = True
                stack.append(i + w)
        if area >= min_area:
            out.append({"x0": x0, "y0": y0, "x1": x1 + 1, "y1": y1 + 1,
                        "area": area})
    out = _merge_boxes(out, merge_gap)
    out.sort(key=lambda r: -r["area"])
    return out


def describe(region, mags, mask, w, e1, e2):
    """Attach severity + coarse label to a region from the diff data.

    Labeling logic (CP1 heuristic, calibrated on the fixture corpus):
    a recolor keeps the element outline aligned (high local edge IoU)
    and fills the box densely; geometry drift (moved / missing / resized)
    either misaligns edges inside the box or only partially fills it.
    """
    x0, y0, x1, y1 = region["x0"], region["y0"], region["x1"], region["y1"]
    mag_sum = 0.0
    mag_n = 0
    hot = 0
    inter = union = 0
    for y in range(y0, y1):
        row = y * w
        for x in range(x0, x1):
            o = row + x
            if mask[o]:
                hot += 1
                mag_sum += mags[o]
                mag_n += 1
            if e1[o] or e2[o]:
                union += 1
                if e1[o] and e2[o]:
                    inter += 1
    mean_mag = mag_sum / mag_n if mag_n else 0.0
    box_area = max(1, (x1 - x0) * (y1 - y0))
    fill = hot / box_area
    local_edge_iou = inter / union if union else 1.0
    if fill >= 0.5 and local_edge_iou >= 0.6:
        label = "color"
    else:
        label = "spacing/layout"
    return {"mean_magnitude": round(mean_mag, 4),
            "fill": round(fill, 4),
            "local_edge_iou": round(local_edge_iou, 4),
            "label": label}
