from pathlib import Path
from typing import Any


class IosData:
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

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "bundle_id": self.bundle_id,
        }
        if self.info_plist:
            data["info_plist"] = self.info_plist
        if self.entitlements:
            data["entitlements"] = self.entitlements
        if self.permissions:
            data["permissions"] = self.permissions
        if self.frameworks:
            data["frameworks"] = self.frameworks
        if self.site_frameworks:
            data["site_frameworks"] = self.site_frameworks
        if self.developer_team is not None:
            data["developer_team"] = self.developer_team
        if self.minimum_deployment is not None:
            data["minimum_deployment"] = self.minimum_deployment
        if self.pre_build is not None:
            data["pre_build"] = str(self.pre_build)
        if self.post_build is not None:
            data["post_build"] = str(self.post_build)
        return data
