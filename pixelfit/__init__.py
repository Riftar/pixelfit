"""pixelfit: measure how closely a built UI matches its design.

Zero-dependency, offline image comparison core with a thin CLI.
"""
__version__ = "0.1.0"

from .core import PROFILES, compare, compare_images  # noqa: F401
