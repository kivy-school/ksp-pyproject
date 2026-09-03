from typing import Any

from ._toml import TomlTable, subtable
from .kivyschool_data import KivySchoolData


class ToolData:

    kivy_school: KivySchoolData | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.kivy_school = (
            KivySchoolData(data["kivy-school"]) if "kivy-school" in data else None
        )

    def dump(self, table: TomlTable) -> None:
        if self.kivy_school is not None:
            self.kivy_school.dump(subtable(table, "kivy-school"))

    def scaffold(self, table: TomlTable, path: str) -> None:
        if self.kivy_school is not None:
            self.kivy_school.scaffold(
                subtable(table, "kivy-school"), f"{path}.kivy-school"
            )
        else:
            KivySchoolData.scaffold_missing(table, f"{path}.kivy-school")

    @classmethod
    def scaffold_missing(cls, table: TomlTable, path: str) -> None:
        KivySchoolData.scaffold_missing(table, f"{path}.kivy-school")
