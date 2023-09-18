try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11


class Architecture(StrEnum):
    x86 = "x86"
    x86_64 = "x86_64"
    armv7 = "armv7"
    armv8 = "armv8"
