from pathlib import Path

from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseType
from .marshal import JavaMarshal
from pydjinni.generator.generator import Generator


class JavaGenerator(Generator, key="java", marshal=JavaMarshal):

    def write_source(self, template: str, type_def: BaseType):
        self.write(
            file=type_def.java.source,
            template=template,
            type_def=type_def
        )

    def generate_enum(self, type_def: Enum):
        self.write_source(template="source/enum.java.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_source(template="source/flags.java.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_source(template="source/record.java.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_source(template="source/interface.java.jinja2", type_def=type_def)
