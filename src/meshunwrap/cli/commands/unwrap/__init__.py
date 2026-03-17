"""CLI entrypoint for UV unwrapping."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from typer import Option, Typer, echo

from meshunwrap.artifacts import load_mesh_artifact, save_uv_artifact
from meshunwrap.workflow import reconstruct_from_input, unwrap_mesh

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def unwrap(
    *,
    mesh_artifact: Annotated[
        Path | None,
        Option("--mesh-artifact", help="Existing reconstruction artifact (.npz)"),
    ] = None,
    input_path: Annotated[
        Path | None,
        Option("--input", "-i", help="Point cloud to reconstruct before unwrapping"),
    ] = None,
    fixture: Annotated[str | None, Option("--fixture", help="Named vendored mesh fixture")] = None,
    output_dir: Annotated[Path, Option("--output-dir", "-o", help="Directory for UV artifacts")] = Path(
        "outputs/unwrap",
    ),
    ring_size: Annotated[
        int | None,
        Option("--ring-size", help="Known ring size for structured tube point clouds"),
    ] = None,
) -> None:
    """Compute UV coordinates for a reconstructed tube mesh."""
    if mesh_artifact is not None:
        mesh = load_mesh_artifact(mesh_artifact)
    else:
        mesh = reconstruct_from_input(input_path=input_path, ring_size=ring_size, fixture=fixture)
    result = unwrap_mesh(mesh)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = save_uv_artifact(result, output_dir / "uv.npz")
    echo(str(artifact))
