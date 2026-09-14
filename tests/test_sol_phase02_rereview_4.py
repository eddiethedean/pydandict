"""Sol verification for the unresolved final-evidence identity contract."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sol008_claimed_candidate_ci_qualifies_the_recorded_package_source():
    record = json.loads((ROOT / "docs/research/phase-0.2-results.json").read_text())
    run = record["ci"]["current_candidate_run"]
    assert run, "final evidence requires actual candidate CI proof"
    commit = run["commit"]
    mismatches = []
    for relative, expected in record["source"]["hashes"].items():
        source = subprocess.run(
            ["git", "show", f"{commit}:src/{relative}"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
        if hashlib.sha256(source).hexdigest() != expected:
            mismatches.append(relative)
    assert not mismatches, (
        f"claimed candidate CI at {commit} qualifies different package source: {mismatches}"
    )
