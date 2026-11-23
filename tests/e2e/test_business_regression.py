"""Conserva las comprobaciones de negocio previas, ahora con autenticación real."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e


def test_existing_business_flows(database, tmp_path):
    report = tmp_path / "results.json"
    result = subprocess.run(
        [sys.executable, "tests_manual/run_checks.py", "--report", str(report)],
        cwd=Path(__file__).resolve().parents[2],
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(report.read_text())
    assert data["status"] == "passed"
    assert data["requests"] == 72
    assert len(data["successful_operations"]) == 19
    assert data["process_restart_persistence"] == "passed"
