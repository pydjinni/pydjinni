from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from .marshal import JavaMarshal


class JavaGenerator(Generator, key="java", marshal=JavaMarshal, writes_source=True):

    def generate_enum(self, type_def: Enum):
        self.write_source(
            template="enum.java.jinja2",
            path=self.marshal.source_path() / type_def.java.source,
            type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_source(
            template="flags.java.jinja2",
            path=self.marshal.source_path() / type_def.java.source,
            type_def=type_def
        )

    def generate_record(self, type_def: Record):
        self.write_source(
            template="record.java.jinja2",
            path=self.marshal.source_path() / type_def.java.source,
            type_def=type_def
        )

    def generate_interface(self, type_def: Interface):
        self.write_source(
            template="interface.java.jinja2",
            path=self.marshal.source_path() / type_def.java.source,
            type_def=type_def
        )
