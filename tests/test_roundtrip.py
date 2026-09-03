"""save() must not disturb anything the user wrote by hand.

Each data class returns its own dict from dump(); PyProjectToml.save() merges
that onto the parsed tomlkit document, so comments, ordering and alignment all
survive. A dict can't see the file it came from, so values still equal to their
defaults are written out explicitly -- the file comes to match the model.
"""

from pathlib import Path

from ksp_pyproject.kivyschool_data.android.arch import Arch
from ksp_pyproject.kivyschool_data.android.service_data import ServiceData
from ksp_pyproject.pyproject_toml import PyProjectToml

COMMENTED = """\
# Build config for the demo app
# second header line
[project]
name = "demoapp"          # keep this in sync with the store listing
version = "0.1.0"

[tool.kivy-school]
# sdl2 is required for the camera plugin
bootstrap = "sdl2"

[tool.kivy-school.ios]
bundle_id = "org.kivyschool.demo"
permissions = [
    "NSCameraUsageDescription",   # scanner screen
    "NSMicrophoneUsageDescription",
]

[tool.kivy-school.android]
package_name = "org.kivyschool.demo"
archs = ["arm64-v8a", "x86_64"]
"""


class TestCommentsSurvive:
    def test_every_comment_is_kept(self, write_toml):
        path = write_toml(COMMENTED)
        PyProjectToml(str(path)).save()
        text = path.read_text()
        for comment in [
            "# Build config for the demo app",
            "# second header line",
            "# keep this in sync with the store listing",
            "# sdl2 is required for the camera plugin",
            "# scanner screen",
        ]:
            assert comment in text

    def test_hand_written_values_are_not_disturbed(self, write_toml):
        path = write_toml(COMMENTED)
        PyProjectToml(str(path)).save()
        text = path.read_text()
        assert 'name = "demoapp"          # keep this in sync with the store listing' in text
        assert 'bootstrap = "sdl2"' in text
        assert 'bundle_id = "org.kivyschool.demo"' in text

    def test_array_formatting_is_preserved(self, write_toml):
        path = write_toml(COMMENTED)
        PyProjectToml(str(path)).save()
        text = path.read_text()
        assert "permissions = [\n" in text
        assert '    "NSCameraUsageDescription",   # scanner screen\n' in text

    def test_table_order_is_preserved(self, write_toml):
        path = write_toml(COMMENTED)
        PyProjectToml(str(path)).save()
        text = path.read_text()
        order = [
            text.index("[project]"),
            text.index("[tool.kivy-school]"),
            text.index("[tool.kivy-school.ios]"),
            text.index("[tool.kivy-school.android]"),
        ]
        assert order == sorted(order)

    def test_save_is_idempotent(self, write_toml):
        """Defaults land on the first save; every save after that is a no-op."""
        path = write_toml(COMMENTED)
        PyProjectToml(str(path)).save()
        once = path.read_text()
        for _ in range(3):
            PyProjectToml(str(path)).save()
        assert path.read_text() == once

    def test_saved_file_still_parses_to_the_same_model(self, write_toml):
        path = write_toml(COMMENTED)
        original = PyProjectToml(str(path))
        original.save()
        reloaded = PyProjectToml(str(path))

        assert reloaded.project.name == original.project.name
        assert reloaded.tool.kivy_school.bootstrap == original.tool.kivy_school.bootstrap
        assert (
            reloaded.tool.kivy_school.apple.ios.permissions
            == original.tool.kivy_school.apple.ios.permissions
        )
        assert (
            reloaded.tool.kivy_school.android.archs
            == original.tool.kivy_school.android.archs
        )


class TestModelEditsReachTheFile:
    def test_edits_land_on_save(self, write_toml):
        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.project.name = "renamed"
        pp.tool.kivy_school.bootstrap = "sdl2_gles"
        pp.tool.kivy_school.android.version_code = 9
        pp.save()

        text = path.read_text()
        assert 'name = "renamed"' in text
        assert 'bootstrap = "sdl2_gles"' in text
        assert "version_code = 9" in text

    def test_an_edited_line_keeps_its_own_comment(self, write_toml):
        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.project.name = "renamed"
        pp.save()
        assert 'name = "renamed"          # keep this in sync with the store listing' in path.read_text()


class TestOptionalKeys:
    IOS = (
        "[project]\n"
        'name = "demoapp"\n'
        "\n"
        "[tool.kivy-school.ios]\n"
        'bundle_id = "org.demo"\n'
    )

    def test_commented_out_key_is_untouched(self, write_toml):
        """A key that exists only as a comment is not a key, so nothing can hit it."""
        src = self.IOS + '# developer_team = "ABC123"   # uncomment for release builds\n'
        path = write_toml(src)
        pp = PyProjectToml(str(path))
        assert pp.tool.kivy_school.apple.ios.developer_team is None
        pp.save()

        text = path.read_text()
        assert '# developer_team = "ABC123"   # uncomment for release builds' in text
        assert "\ndeveloper_team" not in text

    def test_setting_none_leaves_the_existing_key_alone(self, write_toml):
        """dump() omits keys it has no value for, so save() cannot remove one.

        Setting a field to None is a no-op on save. Delete it from .data to
        actually drop the key -- see the test below.
        """
        src = self.IOS + 'developer_team = "ABC123"   # ask ops\n'
        path = write_toml(src)
        pp = PyProjectToml(str(path))
        pp.tool.kivy_school.apple.ios.developer_team = None
        pp.save()

        assert 'developer_team = "ABC123"   # ask ops' in path.read_text()

    def test_removing_a_key_takes_both_halves(self, write_toml):
        """The model is what save() writes, so clearing .data alone is not enough."""
        src = self.IOS + 'developer_team = "ABC123"   # ask ops\n'
        path = write_toml(src)
        pp = PyProjectToml(str(path))
        pp.tool.kivy_school.apple.ios.developer_team = None
        del pp.data["tool"]["kivy-school"]["ios"]["developer_team"]
        pp.save()

        text = path.read_text()
        assert "developer_team" not in text
        assert "# ask ops" not in text
        assert 'bundle_id = "org.demo"' in text

    def test_setting_android_to_none_leaves_the_section(self, write_toml):
        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.tool.kivy_school.android = None
        pp.save()

        assert "[tool.kivy-school.android]" in path.read_text()


class TestDefaultsAreWrittenOut:
    def test_defaults_become_explicit(self, write_toml):
        """A returned dict can't know what the file said, so defaults are written."""
        path = write_toml(COMMENTED)
        PyProjectToml(str(path)).save()
        text = path.read_text()
        assert "version_code = 1" in text
        assert 'presplash_color = "#FFFFFF"' in text
        assert "universal_apk = true" in text

    def test_service_defaults_become_explicit(self, write_toml):
        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.tool.kivy_school.android.services = [ServiceData({"name": "sync"})]
        pp.save()

        text = path.read_text()
        assert 'notification_text = "Background task active"' in text
        assert 'start_type = "START_NOT_STICKY"' in text


class TestDumpWritesIntoTheTable:
    def test_each_class_writes_its_own_keys(self, write_toml):
        import tomlkit

        pp = PyProjectToml(str(write_toml(COMMENTED)))

        table = tomlkit.table()
        pp.project.dump(table)
        assert table["name"] == "demoapp"

        table = tomlkit.table()
        pp.tool.kivy_school.apple.ios.dump(table)
        assert table["bundle_id"] == "org.kivyschool.demo"
        assert "developer_team" not in table

    def test_dump_leaves_the_file_alone_until_save(self, write_toml):
        import tomlkit

        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.dump(tomlkit.document())
        assert path.read_text() == COMMENTED


class TestDumpCoercions:
    def _load(self, write_toml) -> PyProjectToml:
        return PyProjectToml(str(write_toml(COMMENTED)))

    def test_paths_dump_as_strings(self, write_toml):
        pp = self._load(write_toml)
        pp.tool.kivy_school.apple.ios.pre_build = Path("scripts/pre.sh")
        pp.tool.kivy_school.android.sdk_path = Path("/opt/android-sdk")
        pp.save()

        text = Path(pp.file_path).read_text()
        assert 'pre_build = "scripts/pre.sh"' in text
        assert 'sdk_path = "/opt/android-sdk"' in text

    def test_archs_dump_as_plain_strings(self, write_toml):
        pp = self._load(write_toml)
        pp.tool.kivy_school.android.archs = [Arch.ARM64_V8A]
        pp.save()
        assert 'archs = ["arm64-v8a"]' in Path(pp.file_path).read_text()

    def test_include_files_dump_as_nested_lists(self, write_toml):
        pp = self._load(write_toml)
        pp.tool.kivy_school.android.include_files = [("assets", ["a.png", "b.png"])]
        pp.save()
        text = Path(pp.file_path).read_text()
        assert 'include_files = [["assets", ["a.png", "b.png"]]]' in text

    def test_services_are_written_as_a_table_array(self, write_toml):
        pp = self._load(write_toml)
        pp.tool.kivy_school.android.services = [ServiceData({"name": "sync"})]
        pp.save()

        text = Path(pp.file_path).read_text()
        assert "[[tool.kivy-school.android.services]]" in text
        assert 'name = "sync"' in text

    def test_removing_a_service_shrinks_the_array(self, write_toml):
        pp = self._load(write_toml)
        pp.tool.kivy_school.android.services = [
            ServiceData({"name": "sync"}),
            ServiceData({"name": "upload"}),
        ]
        pp.save()

        pp = PyProjectToml(pp.file_path)
        pp.tool.kivy_school.android.services = [ServiceData({"name": "sync"})]
        pp.save()

        again = PyProjectToml(pp.file_path)
        assert [s.name for s in again.tool.kivy_school.android.services] == ["sync"]

    def test_everything_survives_a_reload(self, write_toml):
        pp = self._load(write_toml)
        pp.tool.kivy_school.android.services = [
            ServiceData({"name": "sync", "foreground": True})
        ]
        pp.tool.kivy_school.android.include_files = [("assets", ["a.png"])]
        pp.tool.kivy_school.apple.ios.pre_build = Path("scripts/pre.sh")
        pp.save()

        again = PyProjectToml(pp.file_path)
        android = again.tool.kivy_school.android
        assert [s.name for s in android.services] == ["sync"]
        assert android.services[0].foreground is True
        assert android.include_files == [("assets", ["a.png"])]
        assert again.tool.kivy_school.apple.ios.pre_build == Path("scripts/pre.sh")
