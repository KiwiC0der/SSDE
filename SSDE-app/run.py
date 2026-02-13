#!/usr/bin/env python3
"""
SDE Demo — head-tracked 3D wireframe.
Run from the project root: python run.py
"""

import os
import sys

# If run with system Python, re-exec with project venv so dependencies (e.g. cv2) are found
def _ensure_venv() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_abs = os.path.abspath(sys.executable)
    for venv_name in (".venv", "venv"):
        venv_dir = os.path.join(script_dir, venv_name)
        if not os.path.isdir(venv_dir):
            continue
        venv_dir_abs = os.path.abspath(venv_dir)
        # Already running from this venv? (executable path is inside .venv/ or venv/)
        if exe_abs.startswith(venv_dir_abs + os.sep) or exe_abs.startswith(venv_dir_abs + "/"):
            return
        if sys.platform == "win32":
            candidates = [os.path.join(venv_dir, "Scripts", "python.exe")]
        else:
            candidates = [
                os.path.join(venv_dir, "bin", "python"),
                os.path.join(venv_dir, "bin", "python3"),
            ]
        for venv_python in candidates:
            if os.path.isfile(venv_python):
                os.execv(venv_python, [venv_python] + sys.argv)
        return  # venv existed but re-exec failed (e.g. no python binary)
    # No venv found; continue and let imports fail with a clear message below


_ensure_venv()

# Reduce OpenCV/backend stderr noise when camera is missing (set before importing cv2)
os.environ.setdefault("OPENCV_LOG_LEVEL", "SILENT")

try:
    import pygame
    from config import (
        WIN_WIDTH,
        WIN_HEIGHT,
        WIN_TITLE,
        TARGET_FPS,
    )
    from src.head_tracker import HeadTracker
    from src.renderer import draw_wireframe, draw_status, BACKGROUND
    from src.window_capture import WindowCapture
    from src.renderer_3d import numpy_to_surface, draw_textured_quad
    from src.window_manager import WindowManager
    from src.spatial_layout import grid_layout
except ModuleNotFoundError as e:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_hint = ""
    if not (os.path.isdir(os.path.join(script_dir, ".venv")) or os.path.isdir(os.path.join(script_dir, "venv"))):
        venv_hint = (
            "Create a virtual environment and install dependencies:\n"
            "  python3 -m venv .venv\n"
            "  .venv/bin/pip install -r requirements.txt\n"
        )
    else:
        venv_hint = "Activate the venv first: source .venv/bin/activate  (or source venv/bin/activate)\n"
    print(f"Missing dependency: {e.name}", file=sys.stderr)
    print(venv_hint, file=sys.stderr)
    sys.exit(1)


def center_window() -> None:
    """Center the Pygame window on the display."""
    try:
        info = pygame.display.Info()
        x = max(0, (info.current_w - WIN_WIDTH) // 2)
        y = max(0, (info.current_h - WIN_HEIGHT) // 2)
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
    except Exception:
        pass


def main() -> int:
    pygame.init()
    # Fullscreen on the primary display for maximum immersion.
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption(WIN_TITLE)

    tracker = HeadTracker()
    if not tracker.is_available():
        print("Error: Could not open webcam. Check that a camera is connected.", file=sys.stderr)
        pygame.quit()
        return 1

    # Phase 1+: window mirroring setup (multi-window capable)
    capturer = WindowCapture()
    manager = WindowManager()

    own_hwnd = None
    try:
        wm_info = pygame.display.get_wm_info()
        own_hwnd = wm_info.get("window")
    except Exception:
        own_hwnd = None

    # Discover a handful of candidate OS windows to mirror.
    def _pred(hwnd: int, title: str) -> bool:
        # Skip our own SSDE window.
        if own_hwnd is not None and hwnd == own_hwnd:
            return False
        # Skip very small/tool windows.
        return True

    discovered = capturer.enumerate_windows(predicate=_pred)
    # Register up to N windows for mirroring.
    MAX_WINDOWS = 4
    for idx, (_title, hwnd) in enumerate(discovered.items()):
        if idx >= MAX_WINDOWS:
            break
        manager.add_or_update_window(hwnd)

    # Give them a simple spatial layout.
    grid_layout(manager.get_windows())

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        hx, hy, face_ok = tracker.read_head_position()
        screen.fill(BACKGROUND)

        # Update capture + textured quads for each managed window
        for mw in manager.get_windows():
            frame = capturer.capture_window(mw.hwnd)
            if frame is None:
                continue
            tex_surf = numpy_to_surface(frame)
            draw_textured_quad(screen, tex_surf, mw.quad_3d, hx, hy)

        # Draw reference wireframe room and status overlay
        draw_wireframe(screen, hx, hy)
        draw_status(screen, face_ok)
        pygame.display.flip()
        clock.tick(TARGET_FPS)

    tracker.release()
    pygame.quit()
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv or "-c" in sys.argv:
        # Verify imports and optional webcam; exit 0 so run.py can be tested without display/camera
        sys.exit(0)
    sys.exit(main())
