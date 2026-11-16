"""Tests for the command-line interface."""

from __future__ import annotations

from typer.testing import CliRunner

from scw import __version__
from scw.cli.app import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
    assert "numpy" in result.stdout
    assert "scipy" in result.stdout


def test_doctor_command() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "[ok] numpy" in result.stdout
    assert "[ok] scipy" in result.stdout
    assert "all required dependencies are available" in result.stdout


def test_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "version" in result.stdout
    assert "doctor" in result.stdout
