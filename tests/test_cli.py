import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(path, *, module=True):
    command = [sys.executable, "-m", "fixture_leak_check", str(path)]
    env = dict(os.environ)
    source_root = str(Path(__file__).resolve().parents[1] / "src")
    env["PYTHONPATH"] = source_root + os.pathsep + env.get("PYTHONPATH", "")
    if not module:
        executable = shutil.which("fixture-leak-check")
        if executable is None:
            pytest.skip("installed console script is not available in this environment")
        command = [executable, str(path)]
    return subprocess.run(command, capture_output=True, text=True, check=False, env=env)


def parsed_stdout(result):
    return json.loads(result.stdout)


@pytest.mark.parametrize("module", [True, False], ids=["module", "installed-script"])
def test_clear_input_exits_zero_with_value_free_json(tmp_path, module):
    source = tmp_path / "synthetic-clear.jsonl"
    source.write_text('{"note":"ordinary synthetic fixture"}\n', encoding="utf-8")
    result = run_cli(source, module=module)
    assert result.returncode == 0
    assert parsed_stdout(result) == {"status": "clear", "findings": []}
    assert result.stderr == ""
    assert str(source) not in result.stdout + result.stderr


@pytest.mark.parametrize("module", [True, False], ids=["module", "installed-script"])
def test_findings_exit_one_without_values_source_or_path(tmp_path, module):
    source = tmp_path / "synthetic-private-path.jsonl"
    marker = "synthetic.unique.user@example.test"
    source.write_text(f'{marker}\n4242 4242 4242 4242\n', encoding="utf-8")
    result = run_cli(source, module=module)
    assert result.returncode == 1
    assert parsed_stdout(result) == {
        "status": "findings",
        "findings": [
            {"line": 1, "kind": "email"},
            {"line": 2, "kind": "payment_card"},
        ],
    }
    output = result.stdout + result.stderr
    for forbidden in (marker, "4242 4242 4242 4242", str(source), "private-source-marker"):
        assert forbidden not in output


@pytest.mark.parametrize("module", [True, False], ids=["module", "installed-script"])
def test_missing_input_exits_two_without_path_or_exception_detail(tmp_path, module):
    source = tmp_path / "missing-synthetic-input.jsonl"
    result = run_cli(source, module=module)
    assert result.returncode == 2
    assert parsed_stdout(result) == {"status": "invalid_input"}
    assert str(source) not in result.stdout + result.stderr


def test_unreadable_input_exits_two_without_echo(tmp_path):
    # A directory is not a readable input file on Windows or POSIX.
    source = tmp_path / "synthetic-directory-input"
    source.mkdir()
    result = run_cli(source)
    assert result.returncode == 2
    assert parsed_stdout(result) == {"status": "invalid_input"}
    assert str(source) not in result.stdout + result.stderr


def test_non_utf8_input_exits_two_without_echo(tmp_path):
    source = tmp_path / "synthetic-invalid-encoding.jsonl"
    source.write_bytes(b"synthetic-\xff-input\n")
    result = run_cli(source)
    assert result.returncode == 2
    assert parsed_stdout(result) == {"status": "invalid_input"}
    assert str(source) not in result.stdout + result.stderr


def test_invalid_input_output_contains_no_exception_or_content(tmp_path):
    source = tmp_path / "synthetic-invalid-input.jsonl"
    source.write_bytes(b"never-echo-this-\xff\n")
    result = run_cli(source)
    output = result.stdout + result.stderr
    assert result.returncode == 2
    assert "never-echo-this" not in output
    assert str(source) not in output
    assert "Traceback" not in output
