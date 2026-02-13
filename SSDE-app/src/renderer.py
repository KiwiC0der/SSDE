"""Pygame window and wireframe drawing."""

import pygame

from config import BOX_DEPTH, SCALE
from src.projection import project


LINE_COLOR = (255, 255, 255)
LINE_WIDTH = 2
BACKGROUND = (0, 0, 0)


def _dynamic_box_corners(width: int, height: int) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
    """Compute 3D box corners so the front face nearly fills the screen.

    At hx=hy=0 the projected front rectangle touches the screen with a
    small margin, regardless of the current resolution.
    """

    margin_frac = 0.05  # 5% border around the room
    # Reconstruct the effective scale used in projection.project.
    ref = 600.0
    scale = SCALE * (min(width, height) / ref)

    half_w_screen = width * (0.5 - margin_frac)
    half_h_screen = height * (0.5 - margin_frac)

    half_w_world = half_w_screen / scale
    half_h_world = half_h_screen / scale

    front = [
        (-half_w_world,  half_h_world, 0.0),
        ( half_w_world,  half_h_world, 0.0),
        ( half_w_world, -half_h_world, 0.0),
        (-half_w_world, -half_h_world, 0.0),
    ]
    back = [
        (x, y, BOX_DEPTH) for (x, y, _z) in front
    ]
    return front, back


def draw_wireframe(surface: pygame.Surface, hx: float, hy: float) -> None:
    """Draw the 3D box wireframe with off-axis projection."""
    w, h = surface.get_size()
    front_3d, back_3d = _dynamic_box_corners(w, h)
    proj = lambda x, y, z: project(x, y, z, hx, hy, w, h)

    front_pts = [proj(*p) for p in front_3d]
    back_pts = [proj(*p) for p in back_3d]

    # Edges from front to back
    for i in range(4):
        pygame.draw.line(surface, LINE_COLOR, front_pts[i], back_pts[i], LINE_WIDTH)

    # Front rectangle
    for i in range(4):
        pygame.draw.line(
            surface, LINE_COLOR,
            front_pts[i], front_pts[(i + 1) % 4],
            LINE_WIDTH,
        )
    # Back rectangle
    for i in range(4):
        pygame.draw.line(
            surface, LINE_COLOR,
            back_pts[i], back_pts[(i + 1) % 4],
            LINE_WIDTH,
        )


def draw_status(surface: pygame.Surface, face_detected: bool) -> None:
    """Draw a small status line (face detected or not)."""
    font = pygame.font.Font(None, 28)
    text = "Face detected — move your head" if face_detected else "Looking for face..."
    color = (180, 255, 180) if face_detected else (255, 180, 180)
    img = font.render(text, True, color)
    surface.blit(img, (10, surface.get_height() - 30))
