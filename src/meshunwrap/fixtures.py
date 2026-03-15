"""Load vendored mesh fixtures used by the examples and tests."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from meshunwrap.artifacts import load_mesh_artifact

if TYPE_CHECKING:
    from meshunwrap.geometry import MeshData

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "meshes"
_FIXTURE_FILES = {
    "bent-pipe": "bent-pipe.npz",
    "stanford-bunny": "stanford-bunny.npz",
}


def fixture_directory() -> Path:
    """Return the directory that stores vendored mesh fixtures."""
    return _FIXTURE_DIR


def list_fixtures() -> list[str]:
    """Return the sorted list of available fixture names."""
    return sorted(_FIXTURE_FILES)


def load_fixture_mesh(name: str) -> MeshData:
    """Load a named mesh fixture from the vendored fixture directory."""
    try:
        filename = _FIXTURE_FILES[name]
    except KeyError as exc:
        available = ", ".join(list_fixtures())
        raise ValueError(f"unknown fixture {name!r}; expected one of: {available}") from exc
    return load_mesh_artifact(_FIXTURE_DIR / filename)
