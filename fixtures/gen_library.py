"""Design-library fixtures: one screen, several expected states.

States of the same screen (success / empty / network-error) plus an
unrelated dark dashboard for the unknown-state gate. The impl variants
carry small realistic drift so match must still pick the right state.
Run:  python3 fixtures/gen_library.py   (outputs: fixtures/library/)
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
RED = (220, 38, 38)
DARK = (17, 24, 39)
STAT = (31, 41, 55)
STAT_ACCENT = (59, 130, 246)

CARD_Y, CARD_W, CARD_H, CARD_R = 64, 100, 128, 8
CARD_XS = (16, 130, 244)
BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H, BUTTON_R = 16, 208, 120, 26, 6


def _base(img, with_cards=True, button_color=BUTTON):
    fill_rect(img, 0, 0, W, H, BG)
    fill_rect(img, 0, 0, W, 34, HEADER)
    fill_rect(img, 14, 10, 120, 12, TITLE)
    fill_rect(img, 14, 25, 70, 5, (100, 116, 139))
    if with_cards:
        for x in CARD_XS:
            _card(img, x)
    fill_rounded_rect(img, BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H,
                      BUTTON_R, button_color)
    fill_rect(img, BUTTON_X + 24, BUTTON_Y + 9, BUTTON_W - 48, 8, TITLE)


def _card(img, x):
    fill_rounded_rect(img, x, CARD_Y, CARD_W, CARD_H, CARD_R, CARD)
    fill_circle(img, x + 18, CARD_Y + 22, 8, STAT_ACCENT)
    fill_rect(img, x + 34, CARD_Y + 16, 56, 12, CARD_TITLE)
    for i in range(3):
        fill_rect(img, x + 10, CARD_Y + 44 + i * 12, 80, 6, LINE)
    fill_rect(img, x + 10, CARD_Y + 92, 46, 8, LINE)


def state_success():
    img = Image(W, H, 3)
    _base(img)
    return img


def state_empty():
    img = Image(W, H, 3)
    _base(img, with_cards=False, button_color=(107, 114, 128))
    fill_rounded_rect(img, 80, 96, 200, 64, 8, CARD)
    fill_rect(img, 120, 114, 120, 10, CARD_TITLE)
    fill_rect(img, 140, 132, 80, 6, LINE)
    return img


def state_network_error():
    img = Image(W, H, 3)
    _base(img, button_color=RED)
    fill_rounded_rect(img, 16, 42, 328, 16, 4, RED)
    fill_rect(img, 26, 48, 220, 5, (254, 242, 242))
    return img


def screen_dashboard_unrelated():
    """A different screen entirely: dark analytics dashboard."""
    img = Image(W, H, 3)
    fill_rect(img, 0, 0, W, H, DARK)
    fill_rect(img, 0, 0, W, 34, (10, 15, 25))
    fill_rect(img, 14, 10, 90, 12, TITLE)
    for i, x in enumerate((16, 100, 184, 268)):
        fill_rounded_rect(img, x, 48, 76, 56, 6, STAT)
        fill_rect(img, x + 10, 58, 40, 8, STAT_ACCENT)
        fill_rect(img, x + 10, 78, 56, 10, (148, 163, 184))
    fill_rounded_rect(img, 16, 116, 328, 110, 6, STAT)
    for i in range(5):
        h = 30 + (i * 17) % 70
        fill_rect(img, 40 + i * 60, 216 - h, 36, h, STAT_ACCENT)
    return img


def impl_variants():
    """Screenshots with small realistic drift on top of a state."""
    out = {}
    ok = state_success()
    out["impl-state-success.png"] = ok
    err = state_network_error()
    fill_rounded_rect(err, BUTTON_X, BUTTON_Y + 12, BUTTON_W, BUTTON_H,
                      BUTTON_R, RED)  # button 12px low (no bg erase:
    # draw over; the vacated strip shows drift)
    out["impl-state-error.png"] = err
    out["impl-state-unknown.png"] = screen_dashboard_unrelated()
    return out


def main():
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "library")
    os.makedirs(here, exist_ok=True)
    state_success().save(os.path.join(here, "home.success.png"))
    state_empty().save(os.path.join(here, "home.empty.png"))
    state_network_error().save(os.path.join(here, "home.network-error.png"))
    for name, img in impl_variants().items():
        img.save(os.path.join(here, name))
    manifest = {
        "entries": [
            {"key": "home.success", "image": "home.success.png",
             "tags": ["loaded"]},
            {"key": "home.empty", "image": "home.empty.png",
             "tags": ["no-data"]},
            {"key": "home.network-error", "image": "home.network-error.png",
             "tags": ["error", "offline"]},
        ]
    }
    with open(os.path.join(here, "library.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"wrote library fixtures to {here}")


if __name__ == "__main__":
    main()
