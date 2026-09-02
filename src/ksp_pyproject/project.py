from typing import Any


class Project:
    name: str

    def __init__(self, data: dict[str, Any]) -> None:
        self.name = data["name"]

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
        }
        return data
