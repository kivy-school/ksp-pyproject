from typing import Any

from .._toml import TomlTable, comment_default, comment_section, subtable
from .android import AndroidData
from .apple import AppleData


class KivySchoolData:
    EXAMPLE: dict[str, Any] = {
        "app_name": "My App",
        "bootstrap": "kivy",
    }

    app_name: str | None
    android: AndroidData | None
    apple: AppleData | None
    bootstrap: str

    def __init__(self, data: dict[str, Any]) -> None:
        self.app_name = data.get("app_name")
        self.apple = AppleData(data)
        self.android = (
            AndroidData(data["android"]) if "android" in data else None
        )
        self.bootstrap = data.get("bootstrap", "kivy")

    def dump(self, table: TomlTable) -> None:
        table["bootstrap"] = self.bootstrap
        if self.app_name is not None:
            table["app_name"] = self.app_name
        apple = self.apple
        if apple:
            apple.dump(table)
        android = self.android
        if android:
            android.dump(subtable(table, "android"))

    def scaffold(self, table: TomlTable, path: str) -> None:
        for key, value in self.EXAMPLE.items():
            comment_default(table, key, value)
        
        apple = self.apple
        if apple:
            apple.scaffold(table, path)
        android = self.android
        if android:
            android.scaffold(subtable(table, "android"), f"{path}.android")
        else:
            AndroidData.scaffold_missing(table, f"{path}.android")

    @classmethod
    def scaffold_missing(cls, table: TomlTable, path: str) -> None:
        comment_section(table, path, cls.EXAMPLE)
        AppleData.scaffold_missing(table, path)
        AndroidData.scaffold_missing(table, f"{path}.android")
