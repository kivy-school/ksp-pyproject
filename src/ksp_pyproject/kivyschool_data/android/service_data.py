from typing import Any


class ServiceData:
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

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "entrypoint": self.entrypoint,
            "foreground": self.foreground,
            "start_type": self.start_type,
            "notification_title": self.notification_title,
            "notification_text": self.notification_text,
            "notification_icon": self.notification_icon,
        }
        if self.foreground_service_type is not None:
            data["foreground_service_type"] = self.foreground_service_type
        return data
