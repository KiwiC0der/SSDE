"""Webcam + MediaPipe face landmarker for head position tracking."""

import cv2  # pyright: ignore[reportMissingImports]
import numpy as np

from mediapipe.tasks.python.vision.core.image import Image, ImageFormat  # pyright: ignore[reportMissingImports]
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions  # pyright: ignore[reportMissingImports]
from mediapipe.tasks.python.core.base_options import BaseOptions  # pyright: ignore[reportMissingImports]

from config import (
    WEBCAM_INDEX,
    MEDIAPIPE_LANDMARK_INDEX,
    HEAD_POSITION_SCALE,
)
from src.model_utils import get_model_path


class HeadTracker:
    """Tracks head position from webcam using MediaPipe Face Landmarker (0.10+ API)."""

    def __init__(self, camera_index: int = WEBCAM_INDEX):
        self._cap = cv2.VideoCapture(camera_index)
        model_path = get_model_path()
        opts = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            num_faces=1,
        )
        self._landmarker = FaceLandmarker.create_from_options(opts)
        self._last_hx = 0.0
        self._last_hy = 0.0

    def is_available(self) -> bool:
        """Return True if the camera opened successfully."""
        return self._cap.isOpened()

    def read_head_position(self) -> tuple[float, float, bool]:
        """
        Read one frame and return (hx, hy, detected).
        hx, hy are scaled for projection; if no face, returns last known position.
        """
        ok, frame = self._cap.read()
        if not ok:
            return self._last_hx, self._last_hy, False

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not rgb.flags["C_CONTIGUOUS"]:
            rgb = np.ascontiguousarray(rgb)

        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect(mp_image)

        if not result.face_landmarks or len(result.face_landmarks) == 0:
            return self._last_hx, self._last_hy, False

        landmarks = result.face_landmarks[0]
        if len(landmarks) <= MEDIAPIPE_LANDMARK_INDEX:
            return self._last_hx, self._last_hy, False

        pt = landmarks[MEDIAPIPE_LANDMARK_INDEX]
        hx = (pt.x - 0.5) * 2 * HEAD_POSITION_SCALE
        hy = (pt.y - 0.5) * 2 * HEAD_POSITION_SCALE
        self._last_hx, self._last_hy = hx, hy
        return hx, hy, True

    def release(self) -> None:
        """Release the camera."""
        self._cap.release()
