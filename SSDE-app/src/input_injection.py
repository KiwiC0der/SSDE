"""Windows input injection helpers for SSDE.

This module wraps the Windows `SendInput` API using ctypes to synthesize
mouse events. Higher-level code is expected to:
- compute target window client coordinates
- translate them to absolute screen coordinates
- call `send_mouse_move_click` or similar helpers.
"""

from __future__ import annotations

import ctypes
from typing import Tuple

import win32gui  # type: ignore[import-not-found]


user32 = ctypes.windll.user32


# Structures/modelled after Win32 API documentation.
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_union(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_union),
    ]


INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def _screen_to_absolute(x: int, y: int) -> Tuple[int, int]:
    """Convert screen pixel coordinates to SendInput absolute coords."""

    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    abs_x = int(x * 65535 / max(screen_w - 1, 1))
    abs_y = int(y * 65535 / max(screen_h - 1, 1))
    return abs_x, abs_y


def send_mouse_move_click(screen_x: int, screen_y: int) -> None:
    """Move the mouse to (screen_x, screen_y) and perform a left click."""

    ax, ay = _screen_to_absolute(screen_x, screen_y)

    inputs = (INPUT * 3)()

    # Move
    inputs[0].type = INPUT_MOUSE
    inputs[0].union.mi.dx = ax
    inputs[0].union.mi.dy = ay
    inputs[0].union.mi.mouseData = 0
    inputs[0].union.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
    inputs[0].union.mi.time = 0
    inputs[0].union.mi.dwExtraInfo = None
    # Down
    inputs[1].type = INPUT_MOUSE
    inputs[1].union.mi.dx = 0
    inputs[1].union.mi.dy = 0
    inputs[1].union.mi.mouseData = 0
    inputs[1].union.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
    inputs[1].union.mi.time = 0
    inputs[1].union.mi.dwExtraInfo = None
    # Up
    inputs[2].type = INPUT_MOUSE
    inputs[2].union.mi.dx = 0
    inputs[2].union.mi.dy = 0
    inputs[2].union.mi.mouseData = 0
    inputs[2].union.mi.dwFlags = MOUSEEVENTF_LEFTUP
    inputs[2].union.mi.time = 0
    inputs[2].union.mi.dwExtraInfo = None

    user32.SendInput(3, ctypes.byref(inputs), ctypes.sizeof(INPUT))


def window_client_to_screen(hwnd: int, px: int, py: int) -> Tuple[int, int]:
    """Translate client-area coordinates to absolute screen pixels."""

    point = win32gui.ClientToScreen(hwnd, (px, py))
    return int(point[0]), int(point[1])

