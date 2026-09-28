"""Fail if any tracked Markdown file contains an em-dash (CLAUDE.md hard rule 10)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EM_DASH = "\u2014"


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "*.md", "**/*.md"], check=True, capture_output=True, text=True
    )
    return [Path(line) for line in out.stdout.splitlines() if line]


def main(paths: list[str] | None = None) -> int:
    files = [Path(p) for p in paths] if paths else tracked_markdown()
    bad = 0
    for path in files:
        if path.suffix != ".md" or not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if EM_DASH in line:
                print(f"{path}:{lineno}: em-dash found")
                bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
