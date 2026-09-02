from pathlib import Path
from enum import StrEnum

from .arch import Arch
from .service_data import ServiceData


class AndroidData:
    package_name: str
    archs: list[Arch]

    api: int | None
    min_api: int | None
    sdk: str | None
    ndk: str | None
    ndk_api: int | None

    sdk_path: Path | None
    ndk_path: Path | None
    java_path: Path | None
    global_tools: bool
    global_tools_path: Path | None
    icon: str | None
    presplash: str | None
    presplash_color: str | None
    presplash_lottie: str | None
    permissions: list[str]
    meta_data: dict[str, str]
    gradle_dependencies: list[str]
    gradle_plugins: list[str]
    services: list[ServiceData]
    version_code: int
    version_name: str
    include_files: list[tuple[str, list[str]]]

    pre_build: Path | None
    post_build: Path | None

    byte_compile_python: bool
    universal_apk: bool

    def __init__(self, data: dict):
        self.package_name = data["package_name"]
        self.archs = [Arch(a) for a in data.get("archs", [])]
        self.api = data.get("api")
        self.min_api = data.get("min_api")
        self.sdk = data.get("sdk")
        self.ndk = data.get("ndk")
        self.ndk_api = data.get("ndk_api")
        self.sdk_path = Path(data["sdk_path"]) if data.get("sdk_path") else None
        self.ndk_path = Path(data["ndk_path"]) if data.get("ndk_path") else None
        self.java_path = Path(data["java_path"]) if data.get("java_path") else None
        self.global_tools = bool(data.get("global_tools", False))
        self.global_tools_path = (
            Path(data["global_tools_path"])
            if data.get("global_tools_path")
            else None
        )
        self.icon = data.get("icon")
        self.presplash = data.get("presplash")
        self.presplash_color = (
            data.get("presplash_color")
            if data.get("presplash_color")
            else "#FFFFFF"
        )
        self.presplash_lottie = data.get("presplash_lottie")
        self.permissions = data.get("permissions", [])
        self.meta_data = data.get("meta_data", {})
        self.gradle_dependencies = data.get("gradle_dependencies", [])
        self.gradle_plugins = data.get("gradle_plugins", [])
        raw_includes = data.get("include_files", [])
        self.include_files = []
        for item in raw_includes:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                dest = str(item[0])
                if len(item) == 2 and isinstance(item[1], (list, tuple)):
                    sources = [str(x) for x in item[1]]
                else:
                    sources = [str(x) for x in item[1:]]
                self.include_files.append((dest, sources))
        self.services = [ServiceData(s) for s in data.get("services", [])]
        self.version_code = data.get("version_code", 1)
        self.version_name = data.get("version_name", "1.0")

        self.pre_build = Path(data.get("pre_build")) if "pre_build" in data else None  # type: ignore
        self.post_build = Path(data.get("post_build")) if "post_build" in data else None  # type: ignore

        self.byte_compile_python = bool(data.get("byte_compile_python", True))
        self.universal_apk = bool(data.get("universal_apk", True))

    def kivyschool_root(self, working_dir: Path) -> Path:
        """Root for kivy-school managed tools/caches.

        ``global_tools = False`` (default) → ``<working_dir>/.kivyschool`` (project-local).
        ``global_tools = True``            → ``global_tools_path`` if set, else ``~/.kivyschool``.
        """
        if not self.global_tools:
            return working_dir / ".kivyschool"
        if self.global_tools_path is not None:
            return self.global_tools_path
        return Path.home() / ".kivyschool"




