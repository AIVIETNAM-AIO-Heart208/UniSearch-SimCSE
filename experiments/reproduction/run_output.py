"""Keep reruns separate from the published experiment records."""

from pathlib import Path
from tempfile import mkdtemp


def create_run_dir(root: Path, experiment: str) -> Path:
    parent = root / "outputs" / "reproduction"
    parent.mkdir(parents=True, exist_ok=True)
    return Path(mkdtemp(prefix=f"{experiment}-", dir=parent))
