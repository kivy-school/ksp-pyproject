import tomlkit

from ._toml import subtable
from .project import Project
from .tool_data import ToolData


class PyProjectToml:

    file_path: str
    data: tomlkit.TOMLDocument
    project: Project
    tool: ToolData

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.data = self._load_toml()
        self.project = (
            Project(self.data["project"])
        )
        self.tool = ToolData(self.data.get("tool", {}))

    def _load_toml(self) -> tomlkit.TOMLDocument:
        with open(self.file_path, "r") as f:
            return tomlkit.parse(f.read())

    def dump(self, document: tomlkit.TOMLDocument) -> None:
        if self.project is not None:
            self.project.dump(subtable(document, "project"))
        if self.tool.kivy_school is not None:
            self.tool.dump(subtable(document, "tool"))

    def scaffold(self) -> None:
        """Document every unset optional and missing section as comments.

        Only ever adds commented-out lines, and skips anything already set or
        already mentioned in a comment, so it is safe to run repeatedly.
        """
        if self.project is not None:
            self.project.scaffold(self.data["project"], "project")
        else:
            Project.scaffold_missing(self.data, "project")

        if "tool" in self.data:
            self.tool.scaffold(self.data["tool"], "tool")
        else:
            ToolData.scaffold_missing(self.data, "tool")

    def save(self) -> None:
        """Write the model back, preserving comments, order and formatting."""
        self.dump(self.data)

        with open(self.file_path, "w") as f:
            f.write(tomlkit.dumps(self.data))
