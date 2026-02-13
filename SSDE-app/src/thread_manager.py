"""Threading utilities for SSDE window capture and input."""

from __future__ import annotations

import threading
import time
import queue
from typing import Dict, Mapping, Optional

import numpy as np

from config import TARGET_FPS
from src.window_capture import WindowCapture


FrameMap = Mapping[int, np.ndarray]


class CaptureThread(threading.Thread):
    """Background thread that periodically captures a set of windows."""

    def __init__(self, window_handles: Optional[Dict[int, str]] = None, *, max_queue: int = 2) -> None:
        super().__init__(daemon=True)
        self._capturer = WindowCapture()
        self._handles: Dict[int, str] = window_handles or {}
        self.frames: "queue.Queue[FrameMap]" = queue.Queue(maxsize=max_queue)
        self._running = threading.Event()
        self._running.set()

    def update_handles(self, handles: Dict[int, str]) -> None:
        self._handles = dict(handles)

    def stop(self) -> None:
        self._running.clear()

    def run(self) -> None:
        while self._running.is_set():
            frame_batch: Dict[int, np.ndarray] = {}
            for hwnd in list(self._handles.keys()):
                frame = self._capturer.capture_window(hwnd)
                if frame is not None:
                    frame_batch[hwnd] = frame

            if frame_batch:
                try:
                    self.frames.put_nowait(frame_batch)
                except queue.Full:
                    # Drop oldest to keep latency low.
                    try:
                        _ = self.frames.get_nowait()
                    except queue.Empty:
                        pass
                    try:
                        self.frames.put_nowait(frame_batch)
                    except queue.Full:
                        pass

            time.sleep(1.0 / TARGET_FPS)

