"""save() must not disturb anything the user wrote by hand.

These lean on tomlkit's style-preserving document: the strongest assertion
available is that re-saving an untouched file reproduces it byte for byte.
"""

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
app_name = "Demo App"

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


class TestRoundTrip:
    def test_untouched_save_is_byte_identical(self, write_toml):
        path = write_toml(COMMENTED)
        PyProjectToml(str(path)).save()
        assert path.read_text() == COMMENTED

    def test_comments_survive_an_edit(self, write_toml):
        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.data["project"]["version"] = "0.2.0"
        pp.save()

        text = path.read_text()
        assert 'version = "0.2.0"' in text
        assert "# Build config for the demo app" in text
        assert "# sdl2 is required for the camera plugin" in text
        assert "# keep this in sync with the store listing" in text
        assert "# scanner screen" in text

    def test_edit_changes_only_the_target_line(self, write_toml):
        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.data["project"]["version"] = "0.2.0"
        pp.save()

        before = COMMENTED.splitlines()
        after = path.read_text().splitlines()
        assert len(before) == len(after)
        differing = [i for i, (b, a) in enumerate(zip(before, after)) if b != a]
        assert differing == [4]

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

    def test_repeated_saves_are_stable(self, write_toml):
        path = write_toml(COMMENTED)
        for _ in range(3):
            PyProjectToml(str(path)).save()
        assert path.read_text() == COMMENTED

    def test_model_objects_are_snapshots_not_write_handles(self, write_toml):
        """Assigning to a model attribute does not reach the saved document.

        The data model is built by copying values out of the parsed tables, so
        writes have to go through .data until setters exist.
        """
        path = write_toml(COMMENTED)
        pp = PyProjectToml(str(path))
        pp.project.name = "renamed"
        pp.save()
        assert 'name = "demoapp"' in path.read_text()
