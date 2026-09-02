import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def write_toml(tmp_path):
    """Write TOML text to a temp file and return its path."""

    def _write(text: str, name: str = "pyproject.toml") -> Path:
        path = tmp_path / name
        path.write_text(text)
        return path

    return _write
