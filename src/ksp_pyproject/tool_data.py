from typing import Any

from .kivyschool_data import KivySchoolData


class ToolData:

    kivy_school: KivySchoolData | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.kivy_school = (
            KivySchoolData(data["kivy-school"]) if "kivy-school" in data else None
        )

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.kivy_school:
            data["kivy-school"] = self.kivy_school.dump()
        return data
