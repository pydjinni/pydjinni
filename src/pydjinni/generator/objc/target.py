from .objc.generator import ObjcGenerator
from .objcpp.generator import ObjcppGenerator
from pydjinni.generator.target import Target


class ObjcTarget(Target, key="objc", generators=[ObjcGenerator, ObjcppGenerator]):
    """
    Generate Objective-C interface and Objective-C++ gluecode.

    The output of this can also be used to interface with Swift, when the bridging-header generation is enabled.
    """
