from .objc.generator import ObjcGenerator
from .objcpp.generator import ObjcppGenerator
from pydjinni.generator.target import Target
from pydjinni.parser.ast import Record


class ObjcTarget(Target):
    """
    Generate Objective-C interface and Objective-C++ gluecode.

    The output of this can also be used to interface with Swift, when the bridging-header generation is enabled.
    """
    key = "objc"
    generators = [ObjcGenerator, ObjcppGenerator]
    supported_deriving = {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}
