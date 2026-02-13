"""Persistence helpers for SSDE window layouts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Tuple

from src.window_manager import ManagedWindow


def save_layout(windows: Iterable[ManagedWindow], path: Path) -> None:
    """Write window layout information to a JSON file."""

    data = []
    for mw in windows:
        data.append(
            {
                "hwnd": mw.hwnd,
                "title": mw.title,
                "size": list(mw.size),
                "quad_3d": [list(p) for p in mw.quad_3d],
            }
        )

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_layout(path: Path) -> List[ManagedWindow]:
    """Load window layout data if present; otherwise return empty list."""

    if not path.is_file():
        return []

    raw = json.loads(path.read_text(encoding="utf-8"))
    windows: List[ManagedWindow] = []
    from src.window_manager import ManagedWindow as MW  # avoid circular import at module load

    for item in raw:
        mw = MW(
            hwnd=int(item["hwnd"]),
            title=str(item.get("title") or ""),
            size=tuple(item.get("size", (0, 0))),
            quad_3d=[tuple(p) for p in item.get("quad_3d", [])],
        )
        windows.append(mw)
    return windows

