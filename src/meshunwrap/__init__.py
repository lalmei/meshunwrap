"""Top-level package exports for meshunwrap."""

from __future__ import annotations

from meshunwrap._version import debug_info, get_version
from meshunwrap.artifacts import load_mesh_artifact, load_uv_artifact, save_mesh_artifact, save_uv_artifact
from meshunwrap.cli import cli
from meshunwrap.fixtures import fixture_directory, list_fixtures, load_fixture_mesh
from meshunwrap.geometry import MeshData, load_point_cloud_txt, make_example_mesh, reconstruct_tube_mesh
from meshunwrap.rendering import render_mesh_figure, render_normal_figure, render_uv_figure
from meshunwrap.uv import (
    SeamResult,
    UVResult,
    build_adjacency_from_faces,
    estimate_vertex_normals,
    parameterize_tube,
    solve_latitudes,
    solve_longitudes,
    trace_seam,
)
from meshunwrap.workflow import run_example_pipeline

__all__: list[str] = [
    "MeshData",
    "SeamResult",
    "UVResult",
    "build_adjacency_from_faces",
    "cli",
    "debug_info",
    "estimate_vertex_normals",
    "fixture_directory",
    "get_version",
    "list_fixtures",
    "load_fixture_mesh",
    "load_mesh_artifact",
    "load_point_cloud_txt",
    "load_uv_artifact",
    "make_example_mesh",
    "parameterize_tube",
    "reconstruct_tube_mesh",
    "render_mesh_figure",
    "render_normal_figure",
    "render_uv_figure",
    "run_example_pipeline",
    "save_mesh_artifact",
    "save_uv_artifact",
    "solve_latitudes",
    "solve_longitudes",
    "trace_seam",
]
