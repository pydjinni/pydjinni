from .java.generator import JavaGenerator
from .jni.generator import JniGenerator
from pydjinni.generator.target import Target
from pydjinni.parser.ast import Record


class JavaTarget(Target):
    """
    Generate Java interface and JNI gluecode.

    This target generates a public Java interface as well as the required JNI gluecode to interact with the C++ interface.
    """
    key = "java"
    generators = [JavaGenerator, JniGenerator]
    supported_deriving = {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str, Record.Deriving.parcelable}
