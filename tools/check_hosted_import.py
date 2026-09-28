"""Fail if anything outside evals/ imports the eval-only hosted model adapter (hard rule 1)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERN = re.compile(r"agent[./]adapters[./]hosted\b")
ALLOWED_PREFIXES = ("evals/", "tests/", "tools/check_hosted_import.py")


def tracked_python() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "*.py", "**/*.py"], check=True, capture_output=True, text=True
    )
    return [Path(line) for line in out.stdout.splitlines() if line]


def main(paths: list[str] | None = None) -> int:
    files = [Path(p) for p in paths] if paths else tracked_python()
    bad = 0
    for path in files:
        posix = path.as_posix()
        if path.suffix != ".py" or not path.exists() or posix.startswith(ALLOWED_PREFIXES):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")) and PATTERN.search(stripped):
                print(f"{path}:{lineno}: hosted adapter imported outside evals/")
                bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
