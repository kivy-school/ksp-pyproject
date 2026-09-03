from pathlib import Path
from typing import Any

from ..._toml import TomlTable, comment_default, comment_section


class IosData:
    EXAMPLE: dict[str, Any] = {
        "bundle_id": "org.example.app",
        "info_plist": {},
        "entitlements": {},
        "permissions": [],
        "frameworks": [],
        "site_frameworks": [],
        "developer_team": "ABCDE12345",
        "minimum_deployment": "13.0",
        "pre_build": "scripts/ios_pre_build.py",
        "post_build": "scripts/ios_post_build.py",
    }

    bundle_id: str
    info_plist: dict[str, Any]
    entitlements: dict[str, Any]
    permissions: list[str]
    frameworks: list[str]
    site_frameworks: list[str]
    developer_team: str | None
    minimum_deployment: str | None
    pre_build: Path | None
    post_build: Path | None

    def __init__(self, data: dict[str, Any]) -> None:
        self.bundle_id = data["bundle_id"]
        self.info_plist = data.get("info_plist", {})
        self.entitlements = data.get("entitlements", {})
        self.permissions = data.get("permissions", [])
        self.frameworks = data.get("frameworks", [])
        self.site_frameworks = data.get("site_frameworks", [])
        self.developer_team = data.get("developer_team")
        self.minimum_deployment = data.get("minimum_deployment")
        self.pre_build = Path(data.get("pre_build")) if "pre_build" in data else None  # type: ignore
        self.post_build = Path(data.get("post_build")) if "post_build" in data else None  # type: ignore

    def dump(self, table: TomlTable) -> None:
        table["bundle_id"] = self.bundle_id
        if self.info_plist:
            table["info_plist"] = self.info_plist
        if self.entitlements:
            table["entitlements"] = self.entitlements
        if self.permissions:
            table["permissions"] = self.permissions
        if self.frameworks:
            table["frameworks"] = self.frameworks
        if self.site_frameworks:
            table["site_frameworks"] = self.site_frameworks
        if self.developer_team is not None:
            table["developer_team"] = self.developer_team
        if self.minimum_deployment is not None:
            table["minimum_deployment"] = self.minimum_deployment
        if self.pre_build is not None:
            table["pre_build"] = str(self.pre_build)
        if self.post_build is not None:
            table["post_build"] = str(self.post_build)

    def scaffold(self, table: TomlTable, path: str) -> None:
        for key, value in self.EXAMPLE.items():
            comment_default(table, key, value)

    @classmethod
    def scaffold_missing(cls, table: TomlTable, path: str) -> None:
        comment_section(table, path, cls.EXAMPLE)
