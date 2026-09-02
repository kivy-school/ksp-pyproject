from typing import Any

from .ios import IosData
from .macos import MacosData


class AppleData:

    ios: IosData | None
    macos: MacosData | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.ios = IosData(data["ios"]) if "ios" in data else None
        self.macos = MacosData(data["macos"]) if "macos" in data else None

    def dump(self) -> dict[str, Any]:
        """ios and macos sit directly on the kivy-school table, as parsed."""
        data: dict[str, Any] = {}
        if self.ios:
            data["ios"] = self.ios.dump()
        if self.macos:
            data["macos"] = self.macos.dump()
        return data
