"""Identify the Git base of a checkout or its private source distribution."""

import re
import subprocess
from pathlib import Path
from typing import Optional, Sequence


def base_commit() -> str:
    if Path(".git").exists():
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    revision = Path("BASE_COMMIT.txt").read_text(encoding="ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Invalid Git base recorded in BASE_COMMIT.txt")
    return revision


def working_tree_status(paths: Sequence[Path]) -> Optional[list[str]]:
    if not Path(".git").exists():
        return None
    return subprocess.check_output(
        ["git", "status", "--short", "--untracked-files=all", "--", *paths], text=True
    ).splitlines()
