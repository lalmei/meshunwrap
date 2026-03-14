"""meshunwrap CLI application module.

This package exposes the Typer-based command line interface for
`meshunwrap`.

The console script defined in `pyproject.toml` points at the package-level
`cli` object exported from `src/meshunwrap/__init__.py`,
so users can run:

```bash
meshunwrap [COMMAND] [OPTIONS]
```

or:

```bash
uv run python -m meshunwrap [COMMAND] [OPTIONS]
```

Commands are discovered dynamically from `meshunwrap/cli/commands/`.
Each command package should expose a Typer app named `app`; the registration
layer loads those subcommands automatically at startup.

Subcommands may also define a callback with `@app.callback()` to share setup or
default behavior before nested commands run.
"""

from meshunwrap.cli.main_cli import cli_app as cli

__all__: list[str] = ["cli"]
