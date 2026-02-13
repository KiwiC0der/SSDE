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

    To keep the virtual space visually consistent across resolutions, the
    base SCALE from config is multiplied by a factor derived from the
    current window size. At the original 800x600 this behaves exactly as
    before; on larger fullscreen displays the box grows proportionally.
    """
    d = EYE_DIST + z
    f = EYE_DIST / d
    sx = hx + (x - hx) * f
    sy = hy + (y - hy) * f

    # Normalise to the original 600px reference height used in config.
    ref = 600.0
    scale = SCALE * (min(width, height) / ref)

    px = int(width / 2 + sx * scale)
    py = int(height / 2 + sy * scale)
    return px, py
