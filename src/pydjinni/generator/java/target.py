from .java.generator import JavaGenerator
from .jni.generator import JniGenerator
from pydjinni.generator.target import Target


class JavaTarget(Target, key="java", generators=[JavaGenerator, JniGenerator]):
    """
    Generate Java interface and JNI gluecode

    This target generates a public Java interface as well as the required JNI gluecode to interact with the C++ interface.
    """
