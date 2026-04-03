import subprocess
import sys


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "llm_bench", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "run" in result.stdout


def test_cli_run_help():
    result = subprocess.run(
        [sys.executable, "-m", "llm_bench", "run", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "--models" in result.stdout
    assert "--clis" in result.stdout
    assert "--tiers" in result.stdout
