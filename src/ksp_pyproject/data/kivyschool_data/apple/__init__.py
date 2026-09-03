from typing import Any

from ..._toml import TomlTable, subtable
from .ios import IosData
from .macos import MacosData


class AppleData:

    ios: IosData | None
    macos: MacosData | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.ios = IosData(data["ios"]) if "ios" in data else None
        self.macos = MacosData(data["macos"]) if "macos" in data else None

    def dump(self, table: TomlTable) -> None:
        """ios and macos sit directly on the kivy-school table, as parsed."""
        if self.ios is not None:
            self.ios.dump(subtable(table, "ios"))
        if self.macos is not None:
            self.macos.dump(subtable(table, "macos"))

    def scaffold(self, table: TomlTable, path: str) -> None:
        if self.ios is not None:
            self.ios.scaffold(subtable(table, "ios"), f"{path}.ios")
        else:
            IosData.scaffold_missing(table, f"{path}.ios")

        if self.macos is not None:
            self.macos.scaffold(subtable(table, "macos"), f"{path}.macos")
        else:
            MacosData.scaffold_missing(table, f"{path}.macos")

    @classmethod
    def scaffold_missing(cls, table: TomlTable, path: str) -> None:
        IosData.scaffold_missing(table, f"{path}.ios")
        MacosData.scaffold_missing(table, f"{path}.macos")
