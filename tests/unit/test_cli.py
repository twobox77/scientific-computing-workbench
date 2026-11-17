"""Tests for the command-line interface."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from scw import __version__
from scw.cli.app import app
from scw.experiments import ResultStore, RunRecord

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
    assert "experiments" in result.stdout


def _seed_store(tmp_path) -> None:
    store = ResultStore(tmp_path)
    store.save(RunRecord("run01", "exp", 0, results={"loss": 2.0}, tags=("t",)))


def test_experiments_summary(tmp_path) -> None:
    _seed_store(tmp_path)
    result = runner.invoke(app, ["experiments", "summary", str(tmp_path)])
    assert result.exit_code == 0
    assert "runs       1" in result.stdout
    assert "exp: 1" in result.stdout


def test_experiments_list(tmp_path) -> None:
    _seed_store(tmp_path)
    result = runner.invoke(app, ["experiments", "list", str(tmp_path)])
    assert result.exit_code == 0
    assert "run01" in result.stdout
    assert "exp" in result.stdout


def test_experiments_list_no_match(tmp_path) -> None:
    _seed_store(tmp_path)
    result = runner.invoke(
        app, ["experiments", "list", str(tmp_path), "--experiment", "other"]
    )
    assert result.exit_code == 0
    assert "no runs match" in result.stdout


def test_experiments_show(tmp_path) -> None:
    _seed_store(tmp_path)
    result = runner.invoke(app, ["experiments", "show", "run01", str(tmp_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["run_id"] == "run01"


def test_experiments_best(tmp_path) -> None:
    _seed_store(tmp_path)
    result = runner.invoke(app, ["experiments", "best", "loss", str(tmp_path)])
    assert result.exit_code == 0
    assert "run01" in result.stdout


def test_experiments_missing_store_errors() -> None:
    result = runner.invoke(app, ["experiments", "summary", "/nonexistent/scw-store"])
    assert result.exit_code == 1
    assert "no result store" in result.stderr
