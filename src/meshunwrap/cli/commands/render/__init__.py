"""CLI entrypoint for figure rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from typer import Option, Typer, echo

from meshunwrap.artifacts import load_mesh_artifact, load_uv_artifact
from meshunwrap.rendering import render_mesh_figure, render_normal_figure, render_uv_figure
from meshunwrap.workflow import reconstruct_from_input, unwrap_mesh

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def render(
    *,
    mesh_artifact: Annotated[Path | None, Option("--mesh-artifact", help="Reconstruction artifact (.npz)")] = None,
    uv_artifact: Annotated[Path | None, Option("--uv-artifact", help="UV artifact (.npz)")] = None,
    fixture: Annotated[str | None, Option("--fixture", help="Named vendored mesh fixture")] = None,
    output_dir: Annotated[Path, Option("--output-dir", "-o", help="Directory for rendered figures")] = Path(
        "outputs/render",
    ),
) -> None:
    """Render answer-style figures from saved artifacts."""
    if mesh_artifact is not None and uv_artifact is not None:
        mesh = load_mesh_artifact(mesh_artifact)
        uv_result = load_uv_artifact(uv_artifact)
    elif fixture is not None:
        mesh = reconstruct_from_input(fixture=fixture)
        uv_result = unwrap_mesh(mesh)
    else:
        raise ValueError("provide both --mesh-artifact and --uv-artifact, or pass --fixture")
    output_dir.mkdir(parents=True, exist_ok=True)
    render_mesh_figure(mesh, output_dir / "mesh.png")
    render_normal_figure(mesh, output_dir / "normals.png")
    render_uv_figure(uv_result, output_dir / "uv.png")
    echo(str(output_dir))
