"""Coordinate transforms and input helpers for SSDE.

This module connects:
- screen-space mouse coordinates (Pygame window)
- SSDE's 3D world coordinates
- underlying OS window pixel coordinates

Phase 2 focuses on the math; actual input injection is handled in a
separate helper to keep the transforms testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np

from config import EYE_DIST, SCALE


Vec2 = Tuple[float, float]
Vec3 = Tuple[float, float, float]


@dataclass
class WindowQuad:
    """Simple container for a 3D quad and its backing window geometry."""

    quad_3d: Sequence[Vec3]          # [tl, tr, br, bl]
    window_size: Tuple[int, int]     # (w, h) in pixels
    hwnd: int                        # OS window handle


def screen_to_world_ray(
    screen_x: int,
    screen_y: int,
    hx: float,
    hy: float,
    width: int,
    height: int,
) -> Vec3:
    """Compute a view-space ray direction from a screen-space point.

    We approximate the inverse of the off-axis projection by treating
    the screen-space offset as a direction away from the viewer.
    """

    # Normalise to [-1, 1]
    nx = (screen_x - width / 2) / (width / 2)
    ny = (screen_y - height / 2) / (height / 2)

    # Eye position in world space is (hx, hy, -EYE_DIST).
    # Build a direction that passes through the screen point.
    dir_x = nx / SCALE
    dir_y = ny / SCALE
    dir_z = 1.0
    v = np.array([dir_x, dir_y, dir_z], dtype=float)
    v /= np.linalg.norm(v)
    return float(v[0]), float(v[1]), float(v[2])


def ray_plane_intersection(
    ray_origin: Vec3,
    ray_dir: Vec3,
    plane_point: Vec3,
    plane_normal: Vec3,
) -> Optional[Vec3]:
    """Return intersection of a ray and plane, or None if parallel/behind."""

    ro = np.array(ray_origin, dtype=float)
    rd = np.array(ray_dir, dtype=float)
    pp = np.array(plane_point, dtype=float)
    n = np.array(plane_normal, dtype=float)

    denom = float(np.dot(rd, n))
    if abs(denom) < 1e-6:
        return None

    t = float(np.dot(pp - ro, n) / denom)
    if t < 0:
        return None

    p = ro + rd * t
    return float(p[0]), float(p[1]), float(p[2])


def world_to_quad_uv(point: Vec3, quad: Sequence[Vec3]) -> Optional[Vec2]:
    """Convert a 3D point on a rectangular quad into UV coords in [0,1].

    Assumes quad vertices are given as [tl, tr, br, bl] in CCW order and
    the quad is planar.
    """

    tl, tr, br, bl = [np.array(v, dtype=float) for v in quad]
    p = np.array(point, dtype=float)

    # Build local basis from TL.
    u_axis = tr - tl
    v_axis = bl - tl

    # Solve p - tl = a * u_axis + b * v_axis  -> [a, b] are UV.
    m = np.column_stack((u_axis, v_axis))  # 3x2
    rhs = p - tl

    # Least-squares solve for robustness.
    try:
        coeffs, *_ = np.linalg.lstsq(m, rhs, rcond=None)
    except np.linalg.LinAlgError:
        return None

    u = float(coeffs[0])
    v = float(coeffs[1])

    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        return None
    return u, v


def quad_hit_test(
    ray_origin: Vec3,
    ray_dir: Vec3,
    window_quads: Iterable[WindowQuad],
) -> Optional[Tuple[WindowQuad, Vec2]]:
    """Find the closest intersected quad and its UV coordinates."""

    best_dist = float("inf")
    best_hit: Optional[Tuple[WindowQuad, Vec2]] = None

    for wq in window_quads:
        tl, tr, br, bl = wq.quad_3d
        # Approximate normal from two edges.
        edge1 = np.subtract(tr, tl)
        edge2 = np.subtract(bl, tl)
        n = np.cross(edge1, edge2)
        norm = np.linalg.norm(n)
        if norm < 1e-6:
            continue
        n = n / norm

        hit_point = ray_plane_intersection(ray_origin, ray_dir, tl, (float(n[0]), float(n[1]), float(n[2])))
        if hit_point is None:
            continue

        uv = world_to_quad_uv(hit_point, wq.quad_3d)
        if uv is None:
            continue

        # Use distance along ray as depth.
        hp = np.array(hit_point, dtype=float)
        ro = np.array(ray_origin, dtype=float)
        dist = float(np.linalg.norm(hp - ro))
        if dist < best_dist:
            best_dist = dist
            best_hit = (wq, uv)

    return best_hit


def uv_to_window_pixels(uv: Vec2, window_size: Tuple[int, int]) -> Tuple[int, int]:
    """Convert UV coordinates [0,1]x[0,1] into window pixel coordinates."""

    u, v = uv
    w, h = window_size
    px = int(u * w)
    py = int(v * h)
    return px, py

