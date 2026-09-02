import tomlkit
from .tool_data import ToolData
from .project import Project


class PyProjectToml:

    project: Project
    tool: ToolData

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._load_toml()
        self.project = Project(self.data["project"])
        self.tool = ToolData(self.data.get("tool", {}))

    def _load_toml(self) -> tomlkit.TOMLDocument:
        with open(self.file_path, "r") as f:
            return tomlkit.parse(f.read())

    def save(self):
        """Write the document back, preserving comments, order and formatting."""
        with open(self.file_path, "w") as f:
            f.write(tomlkit.dumps(self.data))
