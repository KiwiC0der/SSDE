"""3D textured quad rendering helpers for SSDE.

This module builds on the existing off-axis projection math in
`src.projection` but focuses on mapping captured window frames (numpy
RGB arrays) onto 3D quads.

For Phase 1 we keep the implementation deliberately simple:
- we place a single axis-aligned quad at a fixed depth inside the box
- we project its 3D corners to 2D using `project`
- we scale the window texture to the projected quad size and blit it

This does not provide full perspective-correct texturing (which would
require OpenGL or a software rasteriser), but is sufficient for a
convincing PoC when the quad is not heavily rotated.
"""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import numpy as np
import pygame

from config import BOX_HALF_WIDTH, BOX_HALF_HEIGHT, BOX_DEPTH
from src.projection import project


Vec3 = Tuple[float, float, float]


def make_front_window_quad(aspect: float, depth: float | None = None) -> Sequence[Vec3]:
    """Return 4 3D points defining a window-aligned quad inside the box.

    The quad is centred in X/Y, facing the viewer, with its size chosen
    to respect the given aspect ratio while fitting inside the front
    face of the box.
    """

    if depth is None:
        # Slightly in front of the box centre so it clearly reads as \"inside\"
        depth = BOX_DEPTH * 0.35

    # Compute half-width/height that respects aspect and stays well inside
    # the front face of the box so quads do not bleed outside the wireframe.
    max_w = BOX_HALF_WIDTH * 0.8
    max_h = BOX_HALF_HEIGHT * 0.8

    # Start from width-limited size, then clamp by height.
    half_w = max_w
    half_h = half_w / aspect
    if half_h > max_h:
        half_h = max_h
        half_w = half_h * aspect

    return [
        (-half_w, half_h, depth),   # top-left
        (half_w, half_h, depth),    # top-right
        (half_w, -half_h, depth),   # bottom-right
        (-half_w, -half_h, depth),  # bottom-left
    ]


def numpy_to_surface(frame_rgb: np.ndarray) -> pygame.Surface:
    """Convert an (H, W, 3) RGB numpy array to a Pygame surface."""

    # Pygame expects (W, H, 3) when using surfarray.make_surface.
    if frame_rgb.ndim != 3 or frame_rgb.shape[2] != 3:
        raise ValueError("frame_rgb must be HxWx3 RGB array")
    return pygame.surfarray.make_surface(np.swapaxes(frame_rgb, 0, 1))


def draw_textured_quad(
    surface: pygame.Surface,
    texture_surf: pygame.Surface,
    quad_3d: Sequence[Vec3],
    hx: float,
    hy: float,
) -> None:
    """Project a 3D quad to screen and blit the given texture onto it.

    Notes:
    - For Phase 1 we assume the quad is axis-aligned and not skewed.
    - We approximate perspective by scaling the texture to the average
      projected width/height and blitting at the projected top-left.
    """

    w, h = surface.get_size()
    corners_2d = [project(*p, hx, hy, w, h) for p in quad_3d]

    # Order: [tl, tr, br, bl]
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = corners_2d

    quad_width = max(abs(x1 - x0), abs(x2 - x3))
    quad_height = max(abs(y2 - y1), abs(y3 - y0))

    if quad_width <= 1 or quad_height <= 1:
        return

    scaled = pygame.transform.smoothscale(texture_surf, (int(quad_width), int(quad_height)))
    surface.blit(scaled, (x0, y0))

