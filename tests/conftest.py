"""Make the project, its source package and test references importable.

``tests/`` is added explicitly so ``import infonce_reference`` also works under
``--import-mode=importlib``, which does not put the test directory on sys.path.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for path in (HERE.parent, HERE.parent / "src", HERE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
