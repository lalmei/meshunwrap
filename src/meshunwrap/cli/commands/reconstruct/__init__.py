from __future__ import annotations

from pathlib import Path

from typer import Option, Typer

from meshunwrap.artifacts import save_mesh_artifact
from meshunwrap.workflow import reconstruct_from_input

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def reconstruct(
    input_path: Path | None = Option(None, "--input", "-i", help="Path to a 3-column point cloud text file"),
    output_dir: Path = Option(Path("outputs/reconstruct"), "--output-dir", "-o", help="Directory for artifacts"),
    ring_size: int | None = Option(None, "--ring-size", help="Known ring size for structured tube point clouds"),
) -> None:
    """Reconstruct a tube mesh from a structured point cloud."""
    mesh = reconstruct_from_input(input_path=input_path, ring_size=ring_size)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = save_mesh_artifact(mesh, output_dir / "reconstruction.npz")
    print(artifact)
