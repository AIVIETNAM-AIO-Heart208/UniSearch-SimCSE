"""Make ``src/`` and ``tests/`` importable without ``pip install -e .``.

``tests/`` is added explicitly so ``import infonce_reference`` also works under
``--import-mode=importlib``, which does not put the test directory on sys.path.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for path in (HERE.parent / "src", HERE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
