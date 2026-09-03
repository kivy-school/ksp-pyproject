import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ksp_pyproject.data.kivyschool_data import KivySchoolData
from ksp_pyproject.data.kivyschool_data.android import AndroidData
from ksp_pyproject.data.kivyschool_data.apple.ios import IosData
from ksp_pyproject.data.kivyschool_data.apple.macos import MacosData
from ksp_pyproject.data.project import Project
from ksp_pyproject.data.pyproject_toml import PyProjectToml


@pytest.fixture
def write_toml(tmp_path):
    """Write TOML text to a temp file and return its path."""

    def _write(text: str, name: str = "pyproject.toml") -> Path:
        path = tmp_path / name
        path.write_text(text)
        return path

    return _write


# --- narrowing helpers -------------------------------------------------------
# Every section on the model is optional, so `pp.tool.kivy_school.android.x`
# is a type error and an editor warning even when the fixture TOML clearly has
# the section. These assert the section is present and hand back the non-None
# value, so tests can reach into a known-populated file without a chain of
# `assert ... is not None` at every call site.


def project_of(pp: PyProjectToml) -> Project:
    assert pp.project is not None, "[project] table is missing"
    return pp.project


def kivy_school(pp: PyProjectToml) -> KivySchoolData:
    assert pp.tool.kivy_school is not None, "[tool.kivy-school] is missing"
    return pp.tool.kivy_school


def ios(pp: PyProjectToml) -> IosData:
    apple = kivy_school(pp).apple
    assert apple is not None and apple.ios is not None, "[tool.kivy-school.ios] is missing"
    return apple.ios


def macos(pp: PyProjectToml) -> MacosData:
    apple = kivy_school(pp).apple
    assert apple is not None and apple.macos is not None, "[tool.kivy-school.macos] is missing"
    return apple.macos


def android(pp: PyProjectToml) -> AndroidData:
    a = kivy_school(pp).android
    assert a is not None, "[tool.kivy-school.android] is missing"
    return a
