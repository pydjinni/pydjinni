from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Interface, Record, Flags, Enum
from .marshal import ObjcppMarshal


class ObjcppGenerator(Generator, key="objcpp", marshal=ObjcppMarshal):
    def generate_enum(self, type_def: Enum):
        pass

    def generate_flags(self, type_def: Flags):
        pass

    def generate_record(self, type_def: Record):
        pass

    def generate_interface(self, type_def: Interface):
        pass

    ...
