from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_legacy_qa_script_matches_current_phase3_structure():
    result = subprocess.run(
        ["python3", "scripts/12_qa.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "phase3: preamble.tex missing \\origsecnum macro" not in output
    assert "phase3: main.tex doesn't \\input{preamble}" not in output
    assert "phase3: chapters/ch01.tex missing \\chapter{...}" not in output
    assert "phase4: appendix/1 first note is 2 (not 1)" not in output
    assert "pages have mean_conf < 70 with >30 tokens" not in output
