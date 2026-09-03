from typing import Any

from ._toml import TomlTable, comment_default, comment_section


class Project:
    EXAMPLE: dict[str, Any] = {
        "name": "my-app",
    }

    name: str

    def __init__(self, data: dict[str, Any]) -> None:
        self.name = data["name"]

    def dump(self, table: TomlTable) -> None:
        table["name"] = self.name

    def scaffold(self, table: TomlTable, path: str) -> None:
        for key, value in self.EXAMPLE.items():
            comment_default(table, key, value)

    @classmethod
    def scaffold_missing(cls, table: TomlTable, path: str) -> None:
        comment_section(table, path, cls.EXAMPLE)
