"""Spatial layout helpers for arranging windows in SSDE."""

from __future__ import annotations

from typing import Iterable, Tuple

from src.window_manager import ManagedWindow
from src.renderer_3d import make_front_window_quad


def grid_layout(windows: Iterable[ManagedWindow], columns: int = 2, row_spacing: float = 0.2, depth: float | None = None) -> None:
    """Assign quads for windows in a simple grid in front of the viewer.

    This mutates the `quad_3d` of each ManagedWindow in-place.
    """

    col = 0
    row = 0
    for mw in windows:
        w, h = mw.size
        aspect = w / float(h) if h else 1.0
        base_quad = make_front_window_quad(aspect, depth=depth)

        # Offset in X/Y based on grid coordinates. Keep quads comfortably
        # inside the wireframe box by using modest spacing.
        x_offset = (col - (columns - 1) / 2.0) * 3.0
        y_offset = -row * (2.5 + row_spacing)

        mw.quad_3d = [
            (x + x_offset, y + y_offset, z) for (x, y, z) in base_quad
        ]

        col += 1
        if col >= columns:
            col = 0
            row += 1

