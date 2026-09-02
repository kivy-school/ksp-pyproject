
from .android import AndroidData
from .apple import AppleData


class KivySchoolData:

    app_name: str | None
    android: AndroidData | None
    apple: AppleData | None
    bootstrap: str

    def __init__(self, data: dict):
        self.app_name = data.get("app_name")
        self.apple = AppleData(data)
        self.android = (
            AndroidData(data["android"]) if "android" in data else None
        )
        self.bootstrap = data.get("bootstrap", "kivy")

