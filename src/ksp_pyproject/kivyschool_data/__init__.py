from typing import Any

from .android import AndroidData
from .apple import AppleData


class KivySchoolData:

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

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "bootstrap": self.bootstrap,
        }
        if self.app_name:
            data["app_name"] = self.app_name
        data.update(self.apple.dump())
        if self.android:
            data["android"] = self.android.dump()
        return data
