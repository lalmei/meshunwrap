"""CLI entrypoint for the demo pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from typer import Option, Typer, echo

from meshunwrap.workflow import run_example_pipeline

app = Typer(add_completion=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def run_example(
    *,
    output_dir: Annotated[Path, Option("--output-dir", "-o", help="Directory for example outputs")] = Path(
        "outputs/example",
    ),
    overwrite: Annotated[bool, Option("--overwrite", help="Allow writing into a non-empty output directory")] = False,
    fixture: Annotated[str | None, Option("--fixture", help="Named vendored mesh fixture")] = None,
) -> None:
    """Run the built-in curved tube example end-to-end."""
    paths = run_example_pipeline(output_dir=output_dir, overwrite=overwrite, fixture=fixture)
    echo(str(paths.output_dir))
