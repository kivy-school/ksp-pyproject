from pathlib import Path
from typing import Any

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

    def __init__(self, data: dict[str, Any]) -> None:
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


    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "package_name": self.package_name,
            "global_tools": self.global_tools,
            "presplash_color": self.presplash_color,
            "version_code": self.version_code,
            "version_name": self.version_name,
            "byte_compile_python": self.byte_compile_python,
            "universal_apk": self.universal_apk,
        }

        if self.archs:
            data["archs"] = [arch.value for arch in self.archs]
        if self.permissions:
            data["permissions"] = self.permissions
        if self.meta_data:
            data["meta_data"] = self.meta_data
        if self.gradle_dependencies:
            data["gradle_dependencies"] = self.gradle_dependencies
        if self.gradle_plugins:
            data["gradle_plugins"] = self.gradle_plugins

        if self.include_files:
            include_files: list[list[Any]] = []
            for dest, sources in self.include_files:
                include_files.append([dest, list(sources)])
            data["include_files"] = include_files

        if self.services:
            services: list[dict[str, Any]] = []
            for service in self.services:
                services.append(service.dump())
            data["services"] = services

        if self.api is not None:
            data["api"] = self.api
        if self.min_api is not None:
            data["min_api"] = self.min_api
        if self.sdk is not None:
            data["sdk"] = self.sdk
        if self.ndk is not None:
            data["ndk"] = self.ndk
        if self.ndk_api is not None:
            data["ndk_api"] = self.ndk_api
        if self.sdk_path is not None:
            data["sdk_path"] = str(self.sdk_path)
        if self.ndk_path is not None:
            data["ndk_path"] = str(self.ndk_path)
        if self.java_path is not None:
            data["java_path"] = str(self.java_path)
        if self.global_tools_path is not None:
            data["global_tools_path"] = str(self.global_tools_path)
        if self.icon is not None:
            data["icon"] = self.icon
        if self.presplash is not None:
            data["presplash"] = self.presplash
        if self.presplash_lottie is not None:
            data["presplash_lottie"] = self.presplash_lottie
        if self.pre_build is not None:
            data["pre_build"] = str(self.pre_build)
        if self.post_build is not None:
            data["post_build"] = str(self.post_build)

        return data

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




