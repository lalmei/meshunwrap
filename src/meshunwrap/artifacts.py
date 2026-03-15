"""Read and write persisted mesh and UV artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from meshunwrap.geometry import MeshData
from meshunwrap.uv import UVResult, build_adjacency_from_faces


def save_mesh_artifact(mesh: MeshData, path: str | Path) -> Path:
    """Serialize a mesh artifact to a NumPy archive."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        target,
        points=mesh.points,
        faces=mesh.faces,
        normals=mesh.normals,
        metadata=json.dumps(mesh.metadata),
    )
    return target


def load_mesh_artifact(path: str | Path) -> MeshData:
    """Load a mesh artifact from a NumPy archive."""
    data = np.load(path, allow_pickle=True)
    points = np.asarray(data["points"], dtype=float)
    faces = np.asarray(data["faces"], dtype=int)
    normals = np.asarray(data["normals"], dtype=float)
    metadata = json.loads(str(data["metadata"]))
    adjacency = build_adjacency_from_faces(faces, len(points))
    return MeshData(points=points, faces=faces, adjacency=adjacency, normals=normals, metadata=metadata)


def save_uv_artifact(result: UVResult, path: str | Path) -> Path:
    """Serialize UV parameterization outputs to a NumPy archive."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    west = np.array(result.west_of_seam, dtype=object)
    np.savez(
        target,
        uv=result.uv,
        phi_unwrapped=result.phi_unwrapped,
        theta=result.theta,
        north=np.array(result.north, dtype=int),
        south=np.array(result.south, dtype=int),
        seam_path=result.seam_path,
        west_of_seam=west,
    )
    return target


def load_uv_artifact(path: str | Path) -> UVResult:
    """Load UV parameterization outputs from a NumPy archive."""
    data = np.load(path, allow_pickle=True)
    west = [np.asarray(item, dtype=int) for item in data["west_of_seam"].tolist()]
    return UVResult(
        uv=np.asarray(data["uv"], dtype=float),
        phi_unwrapped=np.asarray(data["phi_unwrapped"], dtype=float),
        theta=np.asarray(data["theta"], dtype=float),
        north=int(data["north"]),
        south=int(data["south"]),
        seam_path=np.asarray(data["seam_path"], dtype=int),
        west_of_seam=west,
    )
