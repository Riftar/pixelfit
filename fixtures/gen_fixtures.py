"""Generate deterministic design/implementation fixture pairs.

Renders a synthetic "design" UI screen, then drifted "implementation"
twins with KNOWN perturbations. The ground truth JSON records which
region drifted and how, so tests gate on detection, not on eyeballs.

Run:  python3 fixtures/gen_fixtures.py
Outputs land in fixtures/ (committed, so a fresh clone runs tests with
zero setup; regeneration is byte-identical by construction).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pixelfit.imageops import Image  # noqa: E402
from pixelfit.paint import (fill_circle, fill_rect,  # noqa: E402
                            fill_rounded_rect)

W, H = 360, 240

BG = (244, 245, 247)
HEADER = (31, 41, 55)
TITLE = (229, 231, 235)
CARD = (255, 255, 255)
CARD_TITLE = (17, 24, 39)
LINE = (156, 163, 175)
BUTTON = (37, 99, 235)
BADGE = (5, 150, 105)

CARD_Y, CARD_W, CARD_H, CARD_R = 64, 100, 128, 8
CARD_XS = (16, 130, 244)
BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H, BUTTON_R = 16, 208, 120, 26, 6

VARIANTS = {
    "clean": "identical copy of the design",
    "shift_button": "primary button shifted 14px down",
    "recolor_card": "middle card background recolored",
    "missing_card": "third card missing entirely",
    "spacing": "cards 2 and 3 shifted 10px right",
    "wide_button": "primary button 30px wider",
}

# Ground-truth boxes (x0, y0, x1, y1) that ANY detected drifted region
# must overlap for the perturbation to count as caught. Generous: they
# cover the union of old and new element positions.
GROUND_TRUTH = {
    "shift_button": [BUTTON_X, 196, BUTTON_X + BUTTON_W + 30, 234],
    "recolor_card": [CARD_XS[1], CARD_Y, CARD_XS[1] + CARD_W,
                     CARD_Y + CARD_H],
    "missing_card": [CARD_XS[2] - 2, CARD_Y - 2, CARD_XS[2] + CARD_W + 2,
                     CARD_Y + CARD_H + 2],
    "spacing": [CARD_XS[1], CARD_Y, W - 12, CARD_Y + CARD_H],
    "wide_button": [BUTTON_X, BUTTON_Y - 2, BUTTON_X + BUTTON_W + 32,
                    BUTTON_Y + BUTTON_H + 2],
}


def _card(img, x, tint=CARD):
    fill_rounded_rect(img, x, CARD_Y, CARD_W, CARD_H, CARD_R, tint)
    fill_circle(img, x + 18, CARD_Y + 22, 8, BADGE)
    fill_rect(img, x + 34, CARD_Y + 16, 56, 12, CARD_TITLE)
    for i in range(3):
        fill_rect(img, x + 10, CARD_Y + 44 + i * 12, 80, 6, LINE)
    fill_rect(img, x + 10, CARD_Y + 92, 46, 8, LINE)


def render(variant):
    img = Image(W, H, 3)
    fill_rect(img, 0, 0, W, H, BG)
    fill_rect(img, 0, 0, W, 34, HEADER)
    fill_rect(img, 14, 10, 120, 12, TITLE)
    fill_rect(img, 14, 25, 70, 5, (100, 116, 139))

    card_tints = [CARD, CARD, CARD]
    if variant == "recolor_card":
        card_tints[1] = (250, 215, 215)  # clearly visible red tint
    for idx, x in enumerate(CARD_XS):
        if variant == "missing_card" and idx == 2:
            continue
        if variant == "spacing" and idx > 0:
            x += 10
        _card(img, x, card_tints[idx])

    bx, by, bw = BUTTON_X, BUTTON_Y, BUTTON_W
    if variant == "shift_button":
        by += 14
    if variant == "wide_button":
        bw += 30
    fill_rounded_rect(img, bx, by, bw, BUTTON_H, BUTTON_R, BUTTON)
    fill_rect(img, bx + 24, by + 9, bw - 48, 8, TITLE)
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    img = render("clean")
    img.save(os.path.join(here, "design.png"))
    manifest = {"width": W, "height": H, "variants": VARIANTS,
                "ground_truth": GROUND_TRUTH}
    for name in VARIANTS:
        render(name).save(os.path.join(here, f"impl-{name}.png"))
    with open(os.path.join(here, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    print(f"wrote {len(VARIANTS) + 1} fixture images + manifest.json")


if __name__ == "__main__":
    main()
