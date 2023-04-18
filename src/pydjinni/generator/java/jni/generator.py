from pathlib import Path

from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseType
from .marshal import JniMarshal
from pydjinni.generator.generator import Generator


class JniGenerator(Generator, key="jni", marshal=JniMarshal):
    def write_header(self, template: str, type_def: BaseType):
        self.write(
            file=type_def.jni.header,
            template=Path(template),
            type_def=type_def
        )

    def write_source(self, template: str, type_def: BaseType):
        self.write(
            file=type_def.jni.source,
            template=Path(template),
            type_def=type_def
        )

    def generate_enum(self, type_def: Enum):
        self.write_header(template="header/enum.hpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header(template="header/flags.hpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header(template="header/record.hpp.jinja2", type_def=type_def)
        self.write_source(template="source/record.cpp.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header(template="header/interface.hpp.jinja2", type_def=type_def)
        self.write_source(template="source/interface.cpp.jinja2", type_def=type_def)
