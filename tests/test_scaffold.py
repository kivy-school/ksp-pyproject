"""scaffold() documents unset optionals and missing sections as comments.

It only ever adds commented-out lines. Anything already set, or already named
in a comment, is left alone -- so it is safe to run over and over.
"""

import tomlkit

from ksp_pyproject.pyproject_toml import PyProjectToml

FRESH = """\
[project]
name = "demoapp"
version = "0.1.0"

[build-system]
requires = ["uv_build>=0.12.7,<0.13.0"]
build-backend = "uv_build"
"""

PARTIAL = """\
[project]
name = "demoapp"

[tool.kivy-school]
bootstrap = "sdl2"

[tool.kivy-school.ios]
bundle_id = "org.kivyschool.demo"
"""


def ios_section(text: str) -> str:
    """Just the [tool.kivy-school.ios] block, before the commented macos one."""
    start = text.index("[tool.kivy-school.ios]")
    return text[start : text.index("# [tool.kivy-school.macos]")]


def scaffolded(write_toml, source: str) -> str:
    path = write_toml(source)
    pp = PyProjectToml(str(path))
    pp.scaffold()
    pp.save()
    return path.read_text()


class TestScaffoldingAFreshFile:
    def test_every_section_is_offered(self, write_toml):
        text = scaffolded(write_toml, FRESH)
        for header in [
            "# [tool.kivy-school]",
            "# [tool.kivy-school.ios]",
            "# [tool.kivy-school.macos]",
            "# [tool.kivy-school.android]",
            "# [[tool.kivy-school.android.services]]",
        ]:
            assert header in text

    def test_optional_keys_come_with_example_values(self, write_toml):
        text = scaffolded(write_toml, FRESH)
        assert '# bundle_id = "org.example.app"' in text
        assert '# archs = ["arm64-v8a", "x86_64"]' in text
        assert "# version_code = 1" in text
        assert "# universal_apk = true" in text
        assert "# info_plist = {}" in text

    def test_the_original_content_is_untouched(self, write_toml):
        text = scaffolded(write_toml, FRESH)
        assert text.startswith(FRESH.rstrip("\n"))

    def test_nothing_becomes_a_real_key(self, write_toml):
        text = scaffolded(write_toml, FRESH)
        assert "tool" not in tomlkit.parse(text)

    def test_the_model_still_sees_nothing_configured(self, write_toml):
        path = write_toml(FRESH)
        pp = PyProjectToml(str(path))
        pp.scaffold()
        pp.save()
        assert PyProjectToml(str(path)).tool.kivy_school is None

    def test_sections_are_separated_by_blank_lines(self, write_toml):
        text = scaffolded(write_toml, FRESH)
        assert "\n\n# [tool.kivy-school]" in text
        assert "\n\n# [tool.kivy-school.ios]" in text


class TestScaffoldIsIdempotent:
    def test_running_again_changes_nothing(self, write_toml):
        path = write_toml(FRESH)
        pp = PyProjectToml(str(path))
        pp.scaffold()
        pp.save()
        once = path.read_text()

        for _ in range(3):
            again = PyProjectToml(str(path))
            again.scaffold()
            again.save()

        assert path.read_text() == once

    def test_a_section_is_offered_only_once(self, write_toml):
        text = scaffolded(write_toml, FRESH)
        assert text.count("# [tool.kivy-school.ios]") == 1


class TestScaffoldRespectsWhatIsThere:
    def test_keys_already_set_are_not_commented(self, write_toml):
        text = scaffolded(write_toml, PARTIAL)
        assert '# bootstrap = "kivy"' not in text

        ios = ios_section(text)
        assert "# bundle_id" not in ios
        assert 'bundle_id = "org.kivyschool.demo"' in ios

    def test_existing_sections_get_their_missing_optionals(self, write_toml):
        ios = ios_section(scaffolded(write_toml, PARTIAL))
        assert '# developer_team = "ABCDE12345"' in ios
        assert '# minimum_deployment = "13.0"' in ios

    def test_a_section_that_exists_is_not_offered_again(self, write_toml):
        text = scaffolded(write_toml, PARTIAL)
        assert "# [tool.kivy-school.ios]" not in text
        assert "# [tool.kivy-school.macos]" in text

    def test_a_line_the_user_commented_out_is_left_alone(self, write_toml):
        source = PARTIAL + '# developer_team = "MY-OWN-TEAM"   # ask ops first\n'
        ios = ios_section(scaffolded(write_toml, source))
        assert '# developer_team = "MY-OWN-TEAM"   # ask ops first' in ios
        assert '# developer_team = "ABCDE12345"' not in ios

    def test_a_prose_comment_naming_the_key_also_counts(self, write_toml):
        source = PARTIAL + "# developer_team is injected by CI\n"
        ios = ios_section(scaffolded(write_toml, source))
        assert "# developer_team is injected by CI" in ios
        assert '# developer_team = "ABCDE12345"' not in ios

    def test_matching_is_on_word_boundaries(self, write_toml):
        """A comment mentioning 'scenarios' must not suppress the ios section."""
        source = FRESH + "# covers a few scenarios\n"
        text = scaffolded(write_toml, source)
        assert "# [tool.kivy-school.ios]" in text


class TestScaffoldAndSaveAreSeparate:
    def test_save_alone_adds_no_comments(self, write_toml):
        path = write_toml(FRESH)
        PyProjectToml(str(path)).save()
        assert "# [tool.kivy-school]" not in path.read_text()

    def test_scaffold_survives_a_later_save(self, write_toml):
        path = write_toml(FRESH)
        pp = PyProjectToml(str(path))
        pp.scaffold()
        pp.save()

        again = PyProjectToml(str(path))
        again.save()
        assert "# [tool.kivy-school.android]" in path.read_text()

    def test_a_file_with_no_project_table_still_scaffolds(self, write_toml):
        path = write_toml('[build-system]\nrequires = ["uv_build"]\n')
        pp = PyProjectToml(str(path))
        assert pp.project is None
        pp.scaffold()
        pp.save()

        text = path.read_text()
        assert "# [project]" in text
        assert "# [tool.kivy-school]" in text
