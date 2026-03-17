from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from meshunwrap import (
    build_adjacency_from_faces,
    fixture_directory,
    list_fixtures,
    load_fixture_mesh,
    make_example_mesh,
    parameterize_tube,
    reconstruct_tube_mesh,
    render_mesh_figure,
    render_normal_figure,
    render_uv_figure,
)


def make_cylinder_mesh(
    n_long: int = 8,
    n_ring: int = 20,
    radius: float = 1.0,
    length: float = 4.0,
) -> tuple[np.ndarray, np.ndarray]:
    points = []
    for i in range(n_long):
        z = -0.5 * length + length * i / (n_long - 1)
        for j in range(n_ring):
            angle = 2.0 * math.pi * j / n_ring
            points.append([radius * math.cos(angle), radius * math.sin(angle), z])

    faces = []
    for i in range(n_long - 1):
        for j in range(n_ring):
            a = i * n_ring + j
            b = i * n_ring + (j + 1) % n_ring
            c = (i + 1) * n_ring + j
            d = (i + 1) * n_ring + (j + 1) % n_ring
            faces.append([a, c, b])
            faces.append([b, c, d])

    return np.asarray(points, dtype=float), np.asarray(faces, dtype=int)


def test_requires_connectivity_for_point_cloud() -> None:
    points = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    with pytest.raises(ValueError, match="provide faces or adjacency"):
        parameterize_tube(points)


def test_straight_cylinder_mesh_produces_uvs() -> None:
    points, faces = make_cylinder_mesh()
    result = parameterize_tube(points, faces=faces)

    assert result.uv.shape == (len(points), 2)
    assert math.isclose(result.theta[result.north], 0.0)
    assert math.isclose(result.theta[result.south], math.pi)
    assert np.all(np.isfinite(result.uv))
    assert np.all(result.uv[:, 0] >= -math.pi - 1e-9)
    assert np.all(result.uv[:, 0] < math.pi + 1e-9)


def test_adjacency_only_input_is_supported() -> None:
    points, faces = make_cylinder_mesh()
    adjacency = build_adjacency_from_faces(faces, len(points))
    result = parameterize_tube(points, adjacency=adjacency)

    assert result.uv.shape == (len(points), 2)
    assert result.seam_path[0] == result.north
    assert result.seam_path[-1] == result.south


def test_example_mesh_reconstructs_and_parameterizes() -> None:
    example = make_example_mesh()
    reconstructed = reconstruct_tube_mesh(example.points, ring_size=example.metadata["ring_size"])
    result = parameterize_tube(reconstructed.points, faces=reconstructed.faces, normals=reconstructed.normals)

    assert reconstructed.points.shape == example.points.shape
    assert len(reconstructed.faces) > 0
    assert np.all(np.isfinite(result.theta))
    assert np.all(np.isfinite(result.phi_unwrapped))
    assert len(result.seam_path) > 2


def test_seam_offsets_create_large_longitude_jump() -> None:
    points, faces = make_cylinder_mesh()
    result = parameterize_tube(points, faces=faces)

    jumps = []
    for vertex, west_neighbors in zip(result.seam_path[1:-1], result.west_of_seam):
        for neighbor in west_neighbors:
            jumps.append(result.phi_unwrapped[int(neighbor)] - result.phi_unwrapped[int(vertex)])

    assert jumps
    assert max(abs(jump) for jump in jumps) > math.pi


def test_fixture_inventory_is_stable() -> None:
    assert list_fixtures() == ["bent-pipe", "stanford-bunny"]
    for name in list_fixtures():
        assert (fixture_directory() / f"{name}.npz").exists()


def test_bent_pipe_fixture_unwraps_with_seam() -> None:
    mesh = load_fixture_mesh("bent-pipe")
    result = parameterize_tube(mesh.points, faces=mesh.faces, normals=mesh.normals)

    assert np.all(np.isfinite(result.uv))
    assert len(result.seam_path) > 2
    assert result.seam_path[0] == result.north
    assert result.seam_path[-1] == result.south


def test_stanford_bunny_fixture_unwraps() -> None:
    mesh = load_fixture_mesh("stanford-bunny")
    result = parameterize_tube(mesh.points, faces=mesh.faces, normals=mesh.normals)

    assert np.all(np.isfinite(result.uv))
    assert result.uv.shape == (len(mesh.points), 2)


def test_fixture_rendering_smoke(tmp_path: Path) -> None:
    for name in list_fixtures():
        mesh = load_fixture_mesh(name)
        result = parameterize_tube(mesh.points, faces=mesh.faces, normals=mesh.normals)
        output_dir = tmp_path / name
        mesh_path = render_mesh_figure(mesh, output_dir / "mesh.png")
        normal_path = render_normal_figure(mesh, output_dir / "normals.png")
        uv_path = render_uv_figure(result, output_dir / "uv.png")

        assert mesh_path.exists()
        assert normal_path.exists()
        assert uv_path.exists()
