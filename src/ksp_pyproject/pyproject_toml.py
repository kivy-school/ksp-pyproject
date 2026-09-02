from typing import Any

import tomlkit

from ._toml import merge, subtable
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
        self.project = Project(self.data["project"])
        self.tool = ToolData(self.data.get("tool", {}))

    def _load_toml(self) -> tomlkit.TOMLDocument:
        with open(self.file_path, "r") as f:
            return tomlkit.parse(f.read())

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "project": self.project.dump(),
        }
        tool = self.tool.dump()
        if tool:
            data["tool"] = tool
        return data

    def save(self) -> None:
        """Write the model back, preserving comments, order and formatting."""
        for key, value in self.dump().items():
            merge(subtable(self.data, key), value)

        with open(self.file_path, "w") as f:
            f.write(tomlkit.dumps(self.data))
