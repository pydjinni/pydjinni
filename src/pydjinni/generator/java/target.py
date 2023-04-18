from .java.generator import JavaGenerator
from .jni.generator import JniGenerator
from pydjinni.generator.target import Target


class JavaTarget(Target, key="java", generators=[JavaGenerator, JniGenerator]):
    pass
