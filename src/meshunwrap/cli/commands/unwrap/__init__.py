from __future__ import annotations

from pathlib import Path

from typer import Option, Typer

from meshunwrap.artifacts import load_mesh_artifact, save_uv_artifact
from meshunwrap.workflow import reconstruct_from_input, unwrap_mesh

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def unwrap(
    mesh_artifact: Path | None = Option(None, "--mesh-artifact", help="Existing reconstruction artifact (.npz)"),
    input_path: Path | None = Option(None, "--input", "-i", help="Point cloud to reconstruct before unwrapping"),
    output_dir: Path = Option(Path("outputs/unwrap"), "--output-dir", "-o", help="Directory for UV artifacts"),
    ring_size: int | None = Option(None, "--ring-size", help="Known ring size for structured tube point clouds"),
) -> None:
    """Compute UV coordinates for a reconstructed tube mesh."""
    if mesh_artifact is not None:
        mesh = load_mesh_artifact(mesh_artifact)
    else:
        mesh = reconstruct_from_input(input_path=input_path, ring_size=ring_size)
    result = unwrap_mesh(mesh)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = save_uv_artifact(result, output_dir / "uv.npz")
    print(artifact)
