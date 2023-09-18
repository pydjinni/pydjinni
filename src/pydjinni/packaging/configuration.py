try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11


class Configuration(StrEnum):
    release = "Release"
    debug = "Debug"
    minsizerel = "MinSizeRel"
    relwithdebinfo = "RelWithDebInfo"
