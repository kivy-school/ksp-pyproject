"""Parsing and defaults for the pyproject.toml data model."""

from pathlib import Path

import pytest

from ksp_pyproject.kivyschool_data import KivySchoolData
from ksp_pyproject.kivyschool_data.android import AndroidData
from ksp_pyproject.kivyschool_data.android.arch import Arch
from ksp_pyproject.kivyschool_data.android.service_data import ServiceData
from ksp_pyproject.kivyschool_data.apple.ios import IosData
from ksp_pyproject.kivyschool_data.apple.macos import MacosData
from ksp_pyproject.project import Project
from ksp_pyproject.pyproject_toml import PyProjectToml
from ksp_pyproject.tool_data import ToolData

MINIMAL = """\
[project]
name = "demoapp"
"""

FULL = """\
[project]
name = "demoapp"

[tool.kivy-school]
app_name = "Demo App"
bootstrap = "sdl2"

[tool.kivy-school.ios]
bundle_id = "org.kivyschool.demo"
permissions = ["NSCameraUsageDescription"]

[tool.kivy-school.macos]
bundle_id = "org.kivyschool.demo.mac"

[tool.kivy-school.android]
package_name = "org.kivyschool.demo"
archs = ["arm64-v8a", "x86_64"]
"""


class TestPyProjectToml:
    def test_loads_project_table(self, write_toml):
        pp = PyProjectToml(str(write_toml(MINIMAL)))
        assert pp.project.name == "demoapp"

    def test_tool_absent_leaves_kivy_school_none(self, write_toml):
        pp = PyProjectToml(str(write_toml(MINIMAL)))
        assert pp.tool.kivy_school is None

    def test_parses_nested_kivy_school_tables(self, write_toml):
        ks = PyProjectToml(str(write_toml(FULL))).tool.kivy_school
        assert ks is not None
        assert ks.app_name == "Demo App"
        assert ks.bootstrap == "sdl2"
        assert ks.apple.ios.bundle_id == "org.kivyschool.demo"
        assert ks.apple.macos.bundle_id == "org.kivyschool.demo.mac"
        assert ks.android.package_name == "org.kivyschool.demo"

    def test_missing_project_table_raises(self, write_toml):
        with pytest.raises(KeyError):
            PyProjectToml(str(write_toml('[tool.other]\nx = 1\n')))


class TestProject:
    def test_name_is_required(self):
        with pytest.raises(KeyError):
            Project({})


class TestToolData:
    def test_unrelated_tools_are_ignored(self):
        assert ToolData({"ruff": {"line-length": 88}}).kivy_school is None


class TestKivySchoolData:
    def test_defaults(self):
        ks = KivySchoolData({})
        assert ks.app_name is None
        assert ks.bootstrap == "kivy"
        assert ks.android is None

    def test_apple_is_built_even_when_absent(self):
        """apple is always constructed; its ios/macos are the optional halves."""
        ks = KivySchoolData({})
        assert ks.apple is not None
        assert ks.apple.ios is None
        assert ks.apple.macos is None

    def test_apple_sections_are_read_off_the_kivy_school_table(self):
        ks = KivySchoolData({"ios": {"bundle_id": "a"}, "macos": {"bundle_id": "b"}})
        assert ks.apple.ios.bundle_id == "a"
        assert ks.apple.macos.bundle_id == "b"


class TestIosData:
    def test_bundle_id_is_required(self):
        with pytest.raises(KeyError):
            IosData({})

    def test_defaults(self):
        ios = IosData({"bundle_id": "org.demo"})
        assert ios.info_plist == {}
        assert ios.entitlements == {}
        assert ios.permissions == []
        assert ios.frameworks == []
        assert ios.site_frameworks == []
        assert ios.developer_team is None
        assert ios.minimum_deployment is None
        assert ios.pre_build is None
        assert ios.post_build is None

    def test_build_hooks_become_paths(self):
        ios = IosData({"bundle_id": "org.demo", "pre_build": "scripts/pre.sh"})
        assert ios.pre_build == Path("scripts/pre.sh")


class TestMacosData:
    def test_archs_default_to_universal(self):
        assert MacosData({"bundle_id": "org.demo"}).archs == ["arm64", "x86_64"]

    def test_archs_override(self):
        assert MacosData({"bundle_id": "org.demo", "archs": ["arm64"]}).archs == ["arm64"]


class TestAndroidData:
    def test_package_name_is_required(self):
        with pytest.raises(KeyError):
            AndroidData({})

    def test_defaults(self):
        a = AndroidData({"package_name": "org.demo"})
        assert a.archs == []
        assert a.api is None
        assert a.global_tools is False
        assert a.presplash_color == "#FFFFFF"
        assert a.permissions == []
        assert a.meta_data == {}
        assert a.services == []
        assert a.version_code == 1
        assert a.version_name == "1.0"
        assert a.byte_compile_python is True
        assert a.universal_apk is True

    def test_archs_become_enum_members(self):
        a = AndroidData({"package_name": "org.demo", "archs": ["arm64-v8a", "x86_64"]})
        assert a.archs == [Arch.ARM64_V8A, Arch.X86_64]

    def test_unknown_arch_raises(self):
        with pytest.raises(ValueError):
            AndroidData({"package_name": "org.demo", "archs": ["mips"]})

    def test_empty_presplash_color_falls_back_to_white(self):
        a = AndroidData({"package_name": "org.demo", "presplash_color": ""})
        assert a.presplash_color == "#FFFFFF"

    def test_include_files_pair_form(self):
        a = AndroidData(
            {"package_name": "org.demo", "include_files": [["assets", ["a.png", "b.png"]]]}
        )
        assert a.include_files == [("assets", ["a.png", "b.png"])]

    def test_include_files_varargs_form(self):
        a = AndroidData(
            {"package_name": "org.demo", "include_files": [["assets", "a.png", "b.png"]]}
        )
        assert a.include_files == [("assets", ["a.png", "b.png"])]

    def test_include_files_skips_malformed_entries(self):
        a = AndroidData({"package_name": "org.demo", "include_files": [["assets"], "junk"]})
        assert a.include_files == []


class TestKivySchoolRoot:
    def test_project_local_by_default(self, tmp_path):
        a = AndroidData({"package_name": "org.demo"})
        assert a.kivyschool_root(tmp_path) == tmp_path / ".kivyschool"

    def test_global_tools_without_path_uses_home(self, tmp_path):
        a = AndroidData({"package_name": "org.demo", "global_tools": True})
        assert a.kivyschool_root(tmp_path) == Path.home() / ".kivyschool"

    def test_global_tools_path_wins(self, tmp_path):
        a = AndroidData(
            {
                "package_name": "org.demo",
                "global_tools": True,
                "global_tools_path": str(tmp_path / "shared"),
            }
        )
        assert a.kivyschool_root(tmp_path) == tmp_path / "shared"


class TestServiceData:
    def test_name_is_required(self):
        with pytest.raises(KeyError):
            ServiceData({})

    def test_defaults_derive_from_name(self):
        s = ServiceData({"name": "sync"})
        assert s.entrypoint == "service_main"
        assert s.foreground is False
        assert s.foreground_service_type is None
        assert s.start_type == "START_NOT_STICKY"
        assert s.notification_title == "sync is running"
        assert s.notification_text == "Background task active"
        assert s.notification_icon == "stat_notify_sync"

    def test_entrypoint_path_is_normalised_to_module_syntax(self):
        s = ServiceData({"name": "sync", "entrypoint": "services/main.py"})
        assert s.entrypoint == "services.main"

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("services/main.py", "services.main"),
            ("services/main", "services.main"),
            ("service_main", "service_main"),
            ("a/b/c.py", "a.b.c"),
            # only a trailing ".py" is an extension; these are module names
            ("app/py_utils.py", "app.py_utils"),
            ("my.python_service", "my.python_service"),
            ("deploy.pytest_hooks", "deploy.pytest_hooks"),
            ("pyproject_watcher", "pyproject_watcher"),
        ],
    )
    def test_entrypoint_only_strips_a_trailing_extension(self, raw, expected):
        assert ServiceData({"name": "sync", "entrypoint": raw}).entrypoint == expected
