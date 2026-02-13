"""Minimal window manager core for SSDE.

Phase 3 starts with a simple in-memory registry of windows that SSDE
knows about, each with:
- OS handle
- title and pixel size
- associated 3D quad for rendering
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import win32gui  # type: ignore[import-not-found]

from src.renderer_3d import make_front_window_quad


Vec3 = Tuple[float, float, float]


@dataclass
class ManagedWindow:
    hwnd: int
    title: str
    size: Tuple[int, int]  # (w, h)
    quad_3d: Sequence[Vec3]


class WindowManager:
    """Tracks OS windows and exposes them to the renderer/layout."""

    def __init__(self) -> None:
        self._windows: Dict[int, ManagedWindow] = {}

    # ------------------------------------------------------------------
    # Registration / discovery
    # ------------------------------------------------------------------
    def add_or_update_window(self, hwnd: int) -> ManagedWindow:
        """Ensure a window is tracked and return its descriptor."""

        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        w = max(0, right - left)
        h = max(0, bottom - top)
        title = win32gui.GetWindowText(hwnd)
        if not title:
            title = f"hwnd:{hwnd}"

        if hwnd in self._windows:
            mw = self._windows[hwnd]
            mw.size = (w, h)
            return mw

        aspect = w / float(h) if h else 1.0
        quad = make_front_window_quad(aspect)
        mw = ManagedWindow(hwnd=hwnd, title=title, size=(w, h), quad_3d=quad)
        self._windows[hwnd] = mw
        return mw

    def remove_window(self, hwnd: int) -> None:
        self._windows.pop(hwnd, None)

    def get_windows(self) -> List[ManagedWindow]:
        return list(self._windows.values())

