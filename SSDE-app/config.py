"""Configuration constants for the SDE (Spatial Desktop Envirnoment) demo."""

# Projection
SCALE = 120
EYE_DIST = 8.0

# Window
WIN_WIDTH = 800
WIN_HEIGHT = 600
WIN_TITLE = "SDE (Spatial Desktop Envirnoment) — Head Tracking Demo"

# 3D box (front face z=0, back face z=BOX_DEPTH)
BOX_HALF_WIDTH = 2.0
BOX_HALF_HEIGHT = 1.2
BOX_DEPTH = 6.0

# Head tracking
HEAD_POSITION_SCALE = 5.0  # Multiplier for (hx, hy) from face mesh
MEDIAPIPE_LANDMARK_INDEX = 168  # Nose tip for head position

# Performance
TARGET_FPS = 60
WEBCAM_INDEX = 0


# Window capture / SSDE settings

# Optional substring to identify a default window for mirroring in Phase 1.
# If empty, the app will not attempt automatic selection.
DEFAULT_CAPTURE_WINDOW_KEYWORD = "Notepad"

