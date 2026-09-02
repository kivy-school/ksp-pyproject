from pathlib import Path

class IosData:
    bundle_id: str
    info_plist: dict
    entitlements: dict
    permissions: list[str]
    frameworks: list[str]
    site_frameworks: list[str]
    developer_team: str | None
    minimum_deployment: str | None
    pre_build: Path | None
    post_build: Path | None

    def __init__(self, data: dict):
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
