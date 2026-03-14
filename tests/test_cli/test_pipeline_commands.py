from __future__ import annotations

from pathlib import Path


def test_registered_commands_are_visible(cli_runner, cli_app) -> None:
    result = cli_runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    help_text = result.output
    assert "reconstruct" in help_text
    assert "unwrap" in help_text
    assert "render" in help_text
    assert "run-example" in help_text


def test_run_example_writes_expected_outputs(
    cli_runner, cli_app, tmp_path: Path
) -> None:
    output_dir = tmp_path / "example"
    result = cli_runner.invoke(
        cli_app, ["run-example", "--output-dir", str(output_dir)]
    )
    assert result.exit_code == 0
    assert (output_dir / "curved_pipe_points.txt").exists()
    assert (output_dir / "reconstruction.npz").exists()
    assert (output_dir / "uv.npz").exists()
    assert (output_dir / "mesh.png").exists()
    assert (output_dir / "normals.png").exists()
    assert (output_dir / "uv.png").exists()


def test_unwrap_fixture_writes_uv_artifact(cli_runner, cli_app, tmp_path: Path) -> None:
    output_dir = tmp_path / "fixture-unwrap"
    result = cli_runner.invoke(
        cli_app, ["unwrap", "--fixture", "bent-pipe", "--output-dir", str(output_dir)]
    )
    assert result.exit_code == 0
    assert (output_dir / "uv.npz").exists()


def test_run_example_with_fixture_writes_outputs(
    cli_runner, cli_app, tmp_path: Path
) -> None:
    output_dir = tmp_path / "fixture-example"
    result = cli_runner.invoke(
        cli_app,
        ["run-example", "--fixture", "stanford-bunny", "--output-dir", str(output_dir)],
    )
    assert result.exit_code == 0
    assert not (output_dir / "curved_pipe_points.txt").exists()
    assert (output_dir / "reconstruction.npz").exists()
    assert (output_dir / "uv.npz").exists()
    assert (output_dir / "mesh.png").exists()
    assert (output_dir / "normals.png").exists()
    assert (output_dir / "uv.png").exists()
