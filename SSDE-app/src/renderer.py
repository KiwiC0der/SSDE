"""Pygame window and wireframe drawing."""

import pygame

from config import (
    WIN_WIDTH,
    WIN_HEIGHT,
    WIN_TITLE,
    BOX_HALF_WIDTH,
    BOX_HALF_HEIGHT,
    BOX_DEPTH,
)
from src.projection import project


# 3D corners: front face (z=0) and back face (z=BOX_DEPTH)
FRONT = [
    (-BOX_HALF_WIDTH,  BOX_HALF_HEIGHT, 0),
    ( BOX_HALF_WIDTH,  BOX_HALF_HEIGHT, 0),
    ( BOX_HALF_WIDTH, -BOX_HALF_HEIGHT, 0),
    (-BOX_HALF_WIDTH, -BOX_HALF_HEIGHT, 0),
]
BACK = [
    (-BOX_HALF_WIDTH,  BOX_HALF_HEIGHT, BOX_DEPTH),
    ( BOX_HALF_WIDTH,  BOX_HALF_HEIGHT, BOX_DEPTH),
    ( BOX_HALF_WIDTH, -BOX_HALF_HEIGHT, BOX_DEPTH),
    (-BOX_HALF_WIDTH, -BOX_HALF_HEIGHT, BOX_DEPTH),
]

LINE_COLOR = (255, 255, 255)
LINE_WIDTH = 2
BACKGROUND = (0, 0, 0)


def draw_wireframe(surface: pygame.Surface, hx: float, hy: float) -> None:
    """Draw the 3D box wireframe with off-axis projection."""
    w, h = surface.get_size()
    proj = lambda x, y, z: project(x, y, z, hx, hy, w, h)

    front_pts = [proj(*p) for p in FRONT]
    back_pts = [proj(*p) for p in BACK]

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
