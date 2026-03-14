from __future__ import annotations

from pathlib import Path

from typer import Option, Typer

from meshunwrap.workflow import run_example_pipeline

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def run_example(
    output_dir: Path = Option(Path("outputs/example"), "--output-dir", "-o", help="Directory for example outputs"),
    overwrite: bool = Option(False, "--overwrite", help="Allow writing into a non-empty output directory"),
) -> None:
    """Run the built-in curved tube example end-to-end."""
    paths = run_example_pipeline(output_dir=output_dir, overwrite=overwrite)
    print(paths.output_dir)
