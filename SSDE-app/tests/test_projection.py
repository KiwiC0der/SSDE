"""Quick tests for projection math (no webcam or display needed)."""

import unittest

# Run from project root so config and src are importable
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.projection import project


class TestProjection(unittest.TestCase):
    def test_project_center_at_origin(self):
        """With head at (0,0), center of view should project to screen center."""
        w, h = 800, 600
        px, py = project(0, 0, 0, 0, 0, w, h)
        self.assertEqual(px, w // 2)
        self.assertEqual(py, h // 2)

    def test_project_returns_integers(self):
        """Projected coordinates should be ints for drawing."""
        px, py = project(1.0, -0.5, 2.0, 0.1, 0.2, 800, 600)
        self.assertIsInstance(px, int)
        self.assertIsInstance(py, int)

    def test_farther_z_smaller_scale(self):
        """Point farther in z should project closer to screen center (perspective)."""
        w, h = 800, 600
        cx, cy = w // 2, h // 2
        near = project(1, 1, 0, 0, 0, w, h)
        far = project(1, 1, 10, 0, 0, w, h)
        dist_near = (near[0] - cx) ** 2 + (near[1] - cy) ** 2
        dist_far = (far[0] - cx) ** 2 + (far[1] - cy) ** 2
        self.assertGreater(dist_near, dist_far)


if __name__ == "__main__":
    unittest.main()
