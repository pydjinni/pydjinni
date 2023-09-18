try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11


class Platform(StrEnum):
    windows = "windows"
    linux = "linux"
    macos = "macos"
    ios = "ios"
    ios_simulator = "ios_simulator"
    android = "android"
