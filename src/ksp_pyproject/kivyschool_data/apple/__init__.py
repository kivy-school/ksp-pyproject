from pathlib import Path

from .ios import IosData
from .macos import MacosData

class AppleData:

    def __init__(self, data: dict):
        self.ios = IosData(data["ios"]) if "ios" in data else None
        self.macos = MacosData(data["macos"]) if "macos" in data else None

