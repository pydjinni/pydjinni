from .cpp.generator import CppGenerator
from pydjinni.generator.target import Target


class CppTarget(Target, key="cpp", generators=[CppGenerator]):
    ...
