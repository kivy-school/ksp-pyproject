from pathlib import Path

from .ios import IosData
from .macos import MacosData

class AppleData:

    def __init__(self, ios: IosData | None, macos: MacosData | None):
        self.ios = ios
        self.macos = macos

