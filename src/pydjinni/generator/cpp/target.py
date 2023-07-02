from .cpp.generator import CppGenerator
from pydjinni.generator.target import Target
from pydjinni.parser.ast import Record


class CppTarget(
    Target,
    key="cpp",
    generators=[CppGenerator],
    supported_deriving={Record.Deriving.init, Record.Deriving.eq, Record.Deriving.ord}):
    """
    Generate C++ interfaces.
    """
