"""Mesh reconstruction helpers for structured tubular point clouds."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from meshunwrap.uv import build_adjacency_from_faces, estimate_vertex_normals

if TYPE_CHECKING:
    from pathlib import Path


POINT_DIMENSIONS = 3
POINT_ARRAY_NDIM = 2
FRAME_ALIGNMENT_THRESHOLD = 0.9
MIN_SECTION_COUNT = 4


@dataclass
class MeshData:
    """In-memory representation of a reconstructed triangle mesh."""

    points: np.ndarray
    faces: np.ndarray
    adjacency: list[np.ndarray]
    normals: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)


def load_point_cloud_txt(path: str | Path) -> np.ndarray:
    """Load a three-column text file containing XYZ point positions."""
    points = np.loadtxt(path, dtype=float)
    if points.ndim != POINT_ARRAY_NDIM or points.shape[1] != POINT_DIMENSIONS:
        raise ValueError("point cloud text file must contain three floating-point columns")
    return points


def _principal_axis(points: np.ndarray) -> np.ndarray:
    centered = points - points.mean(axis=0)
    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    axis = vh[0]
    norm = np.linalg.norm(axis)
    if norm == 0.0:
        return np.array([0.0, 0.0, 1.0])
    return axis / norm


def _orthonormal_frame(direction: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    reference = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(reference, direction)) > FRAME_ALIGNMENT_THRESHOLD:
        reference = np.array([0.0, 1.0, 0.0])
    u = reference - np.dot(reference, direction) * direction
    u /= np.linalg.norm(u)
    v = np.cross(direction, u)
    v /= np.linalg.norm(v)
    return u, v


def _candidate_ring_sizes(n_points: int) -> list[int]:
    return [
        divisor
        for divisor in range(6, n_points // 2 + 1)
        if n_points % divisor == 0 and n_points // divisor >= MIN_SECTION_COUNT
    ]


def infer_ring_size(points: np.ndarray) -> int:
    """Infer the per-ring sample count of a structured tubular point cloud."""
    n_points = len(points)
    axis = _principal_axis(points)
    projection = np.sort(points @ axis)
    best_ring_size = 0
    best_score = float("inf")

    for ring_size in _candidate_ring_sizes(n_points):
        n_sections = n_points // ring_size
        grouped = projection.reshape(n_sections, ring_size)
        axial_spread = grouped.std(axis=1).mean()
        centers = grouped.mean(axis=1)
        section_spacing = np.diff(centers).mean() if n_sections > 1 else 1.0
        score = axial_spread / max(section_spacing, 1e-9)
        if score < best_score:
            best_score = score
            best_ring_size = ring_size

    if best_ring_size == 0:
        raise ValueError("unable to infer ring size from point cloud; provide --ring-size explicitly")
    return best_ring_size


def reconstruct_tube_mesh(points: np.ndarray, ring_size: int | None = None) -> MeshData:
    """Connect an ordered tubular point cloud into a triangle mesh."""
    if ring_size is None:
        ring_size = infer_ring_size(points)
    if len(points) % ring_size != 0:
        raise ValueError("point count must be divisible by ring_size")

    axis = _principal_axis(points)
    u, v = _orthonormal_frame(axis)
    axial = points @ axis
    n_sections = len(points) // ring_size
    sorted_indices = np.argsort(axial)
    grouped = sorted_indices.reshape(n_sections, ring_size)

    ordered_sections = []
    for i, section in enumerate(grouped):
        section_points = points[section]
        center = section_points.mean(axis=0)
        if 0 < i < n_sections - 1:
            tangent = points[grouped[i + 1]].mean(axis=0) - points[grouped[i - 1]].mean(axis=0)
            tangent_norm = np.linalg.norm(tangent)
            if tangent_norm > 0.0:
                tangent = tangent / tangent_norm
                u_local, v_local = _orthonormal_frame(tangent)
            else:
                u_local, v_local = u, v
        else:
            u_local, v_local = u, v
        rel = section_points - center
        angles = np.arctan2(rel @ v_local, rel @ u_local)
        ordered_sections.append(section[np.argsort(angles)])

    ordered_indices = np.concatenate(ordered_sections)
    reordered_points = points[ordered_indices]
    inverse = np.empty(len(points), dtype=int)
    inverse[ordered_indices] = np.arange(len(points))

    faces: list[list[int]] = []
    for i in range(n_sections - 1):
        row0 = np.arange(i * ring_size, (i + 1) * ring_size)
        row1 = np.arange((i + 1) * ring_size, (i + 2) * ring_size)
        for j in range(ring_size):
            a = int(row0[j])
            b = int(row0[(j + 1) % ring_size])
            c = int(row1[j])
            d = int(row1[(j + 1) % ring_size])
            faces.append([a, c, b])
            faces.append([b, c, d])

    face_array = np.asarray(faces, dtype=int)
    adjacency = build_adjacency_from_faces(face_array, len(reordered_points))
    normals = estimate_vertex_normals(reordered_points, face_array)
    metadata = {
        "ring_size": ring_size,
        "n_sections": n_sections,
        "source": "reconstructed_point_cloud",
    }
    return MeshData(
        points=reordered_points,
        faces=face_array,
        adjacency=adjacency,
        normals=normals,
        metadata=metadata,
    )


def make_example_mesh(
    n_sections: int = 18,
    ring_size: int = 24,
    radius: float = 0.18,
    length: float = 3.2,
    bend: float = 0.85,
    twist: float = 1.25,
) -> MeshData:
    """Generate a curved tubular mesh used by the demo pipeline."""
    ts = np.linspace(0.0, 1.0, n_sections)
    points = []
    for t in ts:
        center = np.array([bend * np.sin(np.pi * t), 0.15 * np.sin(2.0 * np.pi * t), length * (t - 0.5)])
        tangent = np.array(
            [bend * np.pi * np.cos(np.pi * t), 0.3 * np.pi * np.cos(2.0 * np.pi * t), length],
            dtype=float,
        )
        tangent /= np.linalg.norm(tangent)
        normal, binormal = _orthonormal_frame(tangent)
        angle_offset = twist * np.pi * t
        for j in range(ring_size):
            angle = angle_offset + 2.0 * np.pi * j / ring_size
            offset = radius * (np.cos(angle) * normal + np.sin(angle) * binormal)
            points.append(center + offset)
    point_array = np.asarray(points, dtype=float)
    mesh = reconstruct_tube_mesh(point_array, ring_size=ring_size)
    mesh.metadata.update({"source": "built_in_example"})
    return mesh
