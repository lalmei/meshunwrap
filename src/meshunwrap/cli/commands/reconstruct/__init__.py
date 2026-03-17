"""CLI entrypoint for mesh reconstruction."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from typer import Option, Typer, echo

from meshunwrap.artifacts import save_mesh_artifact
from meshunwrap.workflow import reconstruct_from_input

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def reconstruct(
    *,
    input_path: Annotated[Path | None, Option("--input", "-i", help="Path to a 3-column point cloud text file")] = None,
    fixture: Annotated[str | None, Option("--fixture", help="Named vendored mesh fixture")] = None,
    output_dir: Annotated[Path, Option("--output-dir", "-o", help="Directory for artifacts")] = Path(
        "outputs/reconstruct",
    ),
    ring_size: Annotated[
        int | None,
        Option("--ring-size", help="Known ring size for structured tube point clouds"),
    ] = None,
) -> None:
    """Reconstruct a tube mesh from a structured point cloud."""
    mesh = reconstruct_from_input(input_path=input_path, ring_size=ring_size, fixture=fixture)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = save_mesh_artifact(mesh, output_dir / "reconstruction.npz")
    echo(str(artifact))
