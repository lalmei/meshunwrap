# Architecture

This page describes the generated structure of the `meshunwrap` package.

## Package layout

The generated project keeps reusable logic in `src/meshunwrap/`
and separates optional interfaces by feature flag.

## CLI

When CLI support is enabled, the Typer application lives in
`src/meshunwrap/cli/`.

- `main_cli.py` defines the root Typer app, global options, and context setup.
- `register.py` discovers command packages under `cli/commands/` and registers
  any Typer app exported as `app`.
- Command modules call into core logic in the package; Rich and Typer usage stay
  in the CLI layer.

## Configuration

Shared configuration is loaded through `Config()` in
`src/meshunwrap/config/`.

- `main_config.py` defines the common application settings.

