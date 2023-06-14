from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseType
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

    def generate_loader(self):
        if self.marshal.config.loader:
            package_path = "/".join(self.marshal.config.package.split("."))
            self.write_source(
                template="loader.java.jinja2",
                path=self.marshal.source_path() / package_path / f"{self.marshal.config.loader}.java"
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_loader()
