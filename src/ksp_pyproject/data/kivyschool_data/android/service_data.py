from typing import Any

from ..._toml import TomlTable, comment_default, comment_table_array


class ServiceData:
    EXAMPLE: dict[str, Any] = {
        "name": "sync",
        "entrypoint": "service_main",
        "foreground": False,
        "foreground_service_type": "dataSync",
        "start_type": "START_NOT_STICKY",
        "notification_title": "sync is running",
        "notification_text": "Background task active",
        "notification_icon": "stat_notify_sync",
    }

    name: str
    entrypoint: str
    foreground: bool
    foreground_service_type: str | None
    start_type: str
    notification_title: str
    notification_text: str
    notification_icon: str

    def __init__(self, data: dict[str, Any]) -> None:
        self.name = data["name"]
        # Enforce module syntax if they accidentally leave ".py" or "/"

        raw_entry = data.get("entrypoint", "service_main")
        self.entrypoint = raw_entry.replace("/", ".").removesuffix(".py")
        self.foreground = data.get("foreground", False)
        self.foreground_service_type = data.get("foreground_service_type")
        self.start_type = data.get("start_type", "START_NOT_STICKY")
        self.notification_title = data.get(
            "notification_title", f"{self.name} is running"
        )
        self.notification_text = data.get(
            "notification_text", "Background task active"
        )
        self.notification_icon = data.get(
            "notification_icon", "stat_notify_sync"
        )

    def dump(self, table: TomlTable) -> None:
        table["name"] = self.name
        table["entrypoint"] = self.entrypoint
        table["foreground"] = self.foreground
        table["start_type"] = self.start_type
        table["notification_title"] = self.notification_title
        table["notification_text"] = self.notification_text
        table["notification_icon"] = self.notification_icon
        if self.foreground_service_type is not None:
            table["foreground_service_type"] = self.foreground_service_type

    def scaffold(self, table: TomlTable, path: str) -> None:
        for key, value in self.EXAMPLE.items():
            comment_default(table, key, value)

    @classmethod
    def scaffold_missing(cls, table: TomlTable, path: str) -> None:
        comment_table_array(table, path, cls.EXAMPLE)
