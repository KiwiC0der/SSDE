"""SDE (Spatial Desktop Envirnoment) projection math."""

from config import EYE_DIST, SCALE


def project(
    x: float, y: float, z: float,
    hx: float, hy: float,
    width: int, height: int,
) -> tuple[int, int]:
    """
    Project a 3D point to 2D screen coordinates using off-axis perspective.
    (hx, hy) is the viewer/head position; the projection center follows it.
    """
    d = EYE_DIST + z
    f = EYE_DIST / d
    sx = hx + (x - hx) * f
    sy = hy + (y - hy) * f
    px = int(width / 2 + sx * SCALE)
    py = int(height / 2 + sy * SCALE)
    return px, py
