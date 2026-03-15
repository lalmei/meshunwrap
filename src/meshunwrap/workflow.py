"""High-level workflows that connect reconstruction, unwrapping, and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from meshunwrap.artifacts import load_mesh_artifact, save_mesh_artifact, save_uv_artifact
from meshunwrap.fixtures import load_fixture_mesh
from meshunwrap.geometry import MeshData, load_point_cloud_txt, make_example_mesh, reconstruct_tube_mesh
from meshunwrap.rendering import render_mesh_figure, render_normal_figure, render_uv_figure
from meshunwrap.uv import UVResult, parameterize_tube


@dataclass
class ExampleRunPaths:
    """Filesystem locations produced by the example pipeline."""

    output_dir: Path
    point_cloud_path: Path | None
    reconstruction_path: Path
    uv_path: Path
    mesh_figure_path: Path
    normal_figure_path: Path
    uv_figure_path: Path


def reconstruct_from_input(
    input_path: str | Path | None = None,
    ring_size: int | None = None,
    fixture: str | None = None,
) -> MeshData:
    """Load a fixture or reconstruct a mesh from a point-cloud text file."""
    if fixture is not None:
        return load_fixture_mesh(fixture)
    if input_path is None:
        return make_example_mesh()
    points = load_point_cloud_txt(input_path)
    return reconstruct_tube_mesh(points, ring_size=ring_size)


def unwrap_mesh(mesh: MeshData, pole_axis: int = 2) -> UVResult:
    """Parameterize a reconstructed mesh into UV coordinates."""
    return parameterize_tube(mesh.points, faces=mesh.faces, normals=mesh.normals, pole_axis=pole_axis)


def run_example_pipeline(
    output_dir: str | Path,
    *,
    overwrite: bool = False,
    fixture: str | None = None,
) -> ExampleRunPaths:
    """Run the end-to-end demo pipeline and write all generated artifacts."""
    target_dir = Path(output_dir)
    if target_dir.exists() and any(target_dir.iterdir()) and not overwrite:
        raise FileExistsError(f"{target_dir} already contains files; pass overwrite to replace outputs")
    target_dir.mkdir(parents=True, exist_ok=True)

    point_cloud_path: Path | None = None
    if fixture is None:
        example = make_example_mesh()
        point_cloud_path = target_dir / "curved_pipe_points.txt"
        np.savetxt(point_cloud_path, example.points)
        reconstructed = reconstruct_from_input(point_cloud_path, ring_size=example.metadata["ring_size"])
    else:
        reconstructed = reconstruct_from_input(fixture=fixture)
    reconstruction_path = save_mesh_artifact(reconstructed, target_dir / "reconstruction.npz")
    uv_result = unwrap_mesh(reconstructed)
    uv_path = save_uv_artifact(uv_result, target_dir / "uv.npz")

    mesh_figure_path = render_mesh_figure(reconstructed, target_dir / "mesh.png")
    normal_figure_path = render_normal_figure(reconstructed, target_dir / "normals.png")
    uv_figure_path = render_uv_figure(uv_result, target_dir / "uv.png")

    return ExampleRunPaths(
        output_dir=target_dir,
        point_cloud_path=point_cloud_path,
        reconstruction_path=reconstruction_path,
        uv_path=uv_path,
        mesh_figure_path=mesh_figure_path,
        normal_figure_path=normal_figure_path,
        uv_figure_path=uv_figure_path,
    )


def load_mesh_for_render(mesh_artifact: str | Path) -> MeshData:
    """Load a mesh artifact for downstream rendering commands."""
    return load_mesh_artifact(mesh_artifact)
