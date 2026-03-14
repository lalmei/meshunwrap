from __future__ import annotations

from pathlib import Path

from meshunwrap.artifacts import load_mesh_artifact
from meshunwrap.geometry import MeshData

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "meshes"
_FIXTURE_FILES = {
    "bent-pipe": "bent-pipe.npz",
    "stanford-bunny": "stanford-bunny.npz",
}


def fixture_directory() -> Path:
    return _FIXTURE_DIR


def list_fixtures() -> list[str]:
    return sorted(_FIXTURE_FILES)


def load_fixture_mesh(name: str) -> MeshData:
    try:
        filename = _FIXTURE_FILES[name]
    except KeyError as exc:
        available = ", ".join(list_fixtures())
        raise ValueError(f"unknown fixture {name!r}; expected one of: {available}") from exc
    return load_mesh_artifact(_FIXTURE_DIR / filename)
