

class ServiceData:
    name: str
    entrypoint: str
    foreground: bool
    foreground_service_type: str | None
    start_type: str
    notification_title: str
    notification_text: str
    notification_icon: str

    def __init__(self, data: dict):
        self.name = data["name"]
        # Enforce module syntax if they accidentally leave ".py" or "/"

        raw_entry = data.get("entrypoint", "service_main")
        self.entrypoint = raw_entry.replace("/", ".").replace(".py", "")
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
