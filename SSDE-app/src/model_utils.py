"""Download and path for MediaPipe Face Landmarker model (used by MediaPipe 0.10+)."""

import os
import urllib.request
from pathlib import Path

# Official MediaPipe model (float16)
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_FILENAME = "face_landmarker.task"


def get_model_path() -> str:
    """
    Return path to face_landmarker.task, downloading it to the app's models dir if needed.
    """
    app_dir = Path(__file__).resolve().parent.parent
    models_dir = app_dir / "models"
    model_path = models_dir / MODEL_FILENAME

    if model_path.is_file():
        return str(model_path)

    models_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Face Landmarker model to {model_path} ...")
    urllib.request.urlretrieve(MODEL_URL, model_path)
    print("Done.")
    return str(model_path)
