"""Window capture utilities for SSDE on Windows.

Currently implemented using the `mss` library on top of the Windows
graphics stack. This gives us fast, low-latency capture of rectangular
regions, which we drive from per-window bounding rectangles.

For Phase 1 we:
- enumerate visible top-level windows
- pick one target window (by title or handle)
- capture its contents into a numpy RGB array on demand

Later phases can layer multi-window capture and threading on top of this.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

import mss  # type: ignore[import-not-found]
import numpy as np
import cv2  # type: ignore[import-not-found]

try:
    import win32gui  # type: ignore[import-not-found]
    import win32con  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - hard dependency on Windows
    raise RuntimeError("window_capture.py requires pywin32 on Windows") from exc


WindowMap = Dict[str, int]


class WindowCapture:
    """Lightweight helper for enumerating and capturing Windows windows.

    We intentionally keep this stateless aside from the underlying MSS
    instance so it can be shared across threads later.
    """

    def __init__(self) -> None:
        self._sct = mss.mss()

    # ------------------------------------------------------------------
    # Enumeration
    # ------------------------------------------------------------------
    def enumerate_windows(self, predicate: Optional[Callable[[int, str], bool]] = None) -> WindowMap:
        """Return {title: hwnd} for all visible top-level windows.

        A predicate `(hwnd, title) -> bool` may be supplied to filter
        which windows are included (e.g. skip our own SSDE window).
        """

        windows: WindowMap = {}

        def _callback(hwnd: int, _extra: int) -> None:
            if not win32gui.IsWindowVisible(hwnd):
                return
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            if not (style & win32con.WS_OVERLAPPEDWINDOW):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            if predicate is not None and not predicate(hwnd, title):
                return
            windows[title] = hwnd

        win32gui.EnumWindows(_callback, 0)
        return windows

    # ------------------------------------------------------------------
    # Capture
    # ------------------------------------------------------------------
    def capture_window(self, hwnd: int) -> Optional[np.ndarray]:
        """Capture a single window into an RGB numpy array.

        Returns:
            ndarray of shape (h, w, 3) in RGB order, or None if capture
            failed (e.g. window minimized or off-screen).
        """

        try:
            rect = win32gui.GetWindowRect(hwnd)
        except win32gui.error:
            return None

        left, top, right, bottom = rect
        width = right - left
        height = bottom - top

        if width <= 0 or height <= 0:
            return None

        # Use MSS to grab this rectangle. On Windows this is typically
        # backed by Desktop Duplication / DXGI under the hood.
        monitor = {"top": top, "left": left, "width": width, "height": height}
        try:
            screenshot = self._sct.grab(monitor)
        except OSError:
            # Can fail for protected content / transient conditions.
            return None

        img = np.array(screenshot)
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img


def find_first_window_matching(capturer: WindowCapture, keyword: str) -> Optional[int]:
    """Return the first window handle whose title contains `keyword`."""

    keyword_lower = keyword.lower()

    def pred(hwnd: int, title: str) -> bool:
        return keyword_lower in title.lower()

    windows = capturer.enumerate_windows(predicate=pred)
    if not windows:
        return None
    # Return the first match (order is not guaranteed but sufficient for PoC).
    _, hwnd = next(iter(windows.items()))
    return hwnd

