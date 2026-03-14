from __future__ import annotations

from pathlib import Path

from typer import Option, Typer

from meshunwrap.artifacts import load_mesh_artifact, load_uv_artifact
from meshunwrap.rendering import render_mesh_figure, render_normal_figure, render_uv_figure

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def render(
    mesh_artifact: Path = Option(..., "--mesh-artifact", help="Reconstruction artifact (.npz)"),
    uv_artifact: Path = Option(..., "--uv-artifact", help="UV artifact (.npz)"),
    output_dir: Path = Option(Path("outputs/render"), "--output-dir", "-o", help="Directory for rendered figures"),
) -> None:
    """Render answer-style figures from saved artifacts."""
    mesh = load_mesh_artifact(mesh_artifact)
    uv_result = load_uv_artifact(uv_artifact)
    output_dir.mkdir(parents=True, exist_ok=True)
    render_mesh_figure(mesh, output_dir / "mesh.png")
    render_normal_figure(mesh, output_dir / "normals.png")
    render_uv_figure(uv_result, output_dir / "uv.png")
    print(output_dir)
