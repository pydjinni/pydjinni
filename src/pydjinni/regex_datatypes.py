import re

class CustomRegexType(str):
    pattern = ".*"
    examples = []
    error_message = "..."

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(pattern=cls.pattern)
        if len(cls.examples) > 0:
            field_schema.update(examples=cls.examples)
            
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        regex = re.compile(cls.pattern)
        m = regex.fullmatch(v)
        if not m:
            raise ValueError(f"'{v}' {cls.error_message}")
        return cls(v)

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

class CppNamespace(CustomRegexType):
    pattern = r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))+[a-zA-Z][a-zA-Z0-9_]*$"
    examples = ["test::namespace", "::other::test::namespace"]
    error_message = "is not a valid C++ namespace"

class CppTypename(CustomRegexType):
    pattern = r"^(::)?([a-zA-Z][a-zA-Z0-9_]*(::))*[a-zA-Z][a-zA-Z0-9_]*$"
    examples = ["test::namespace", "::other::test::namespace"]
    error_message = "is not a valid C++ typename"

class JavaPackage(CustomRegexType):
    pattern = r"^[a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_]$"
    examples = ["my.package.name", "other.package.name"]
    error_message = "is not a valid Java package identifier"

class JavaClass(CustomRegexType):
    pattern = r"^([a-z][a-z0-9_]*([.][a-z0-9_]+)+[0-9a-z_][.])?[a-zA-Z][a-zA-Z0-9_]*$"
    error_message = "is not a valid Java class name"

class JavaPrimitive(CustomRegexType):
    pattern = r"^[a-z]*$"
    error_message = "is not a valid Java primitive type name"

class JavaAnnotation(CustomRegexType):
    pattern = r"^@([a-z][a-z0-9_]*(([.][a-z0-9_]+)+[0-9a-z_])?[.])?[a-zA-Z][a-zA-Z0-9_]*$"
    error_message = "is not a valid Java annotation"

class JniTypeSignature(CustomRegexType):
    pattern = r"^(\((\[?[ZBCSIJFD]|(L([a-z][a-z0-9]*\/)*[A-Z][a-zA-Z0-9]*);)*\))?(\[?[ZBCSIJFD]|(L([a-z][a-z0-9]*\/)*[A-Z][a-zA-Z0-9]*);)?$"
    examples = ["(ILjava/lang/String;[I)J"]
    error_message = "is not a valid JNI type signature"
