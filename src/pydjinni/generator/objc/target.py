from .objc.generator import ObjcGenerator
from .objcpp.generator import ObjcppGenerator
from pydjinni.generator.target import Target


class ObjcTarget(Target, key="objc", generators=[ObjcGenerator, ObjcppGenerator]):
    ...
