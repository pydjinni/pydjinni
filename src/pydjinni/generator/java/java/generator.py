from pathlib import Path

from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseType
from .marshal import JavaMarshal


class JavaGenerator(Generator, key="java", marshal=JavaMarshal, writes_source=True):

    def generate_enum(self, type_def: Enum):
        self.write_source("enum.java.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_source("flags.java.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_source("record.java.jinja2", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_source("interface.java.jinja2", type_def=type_def)

    def generate_loader(self):
        if self.marshal.config.native_lib:
            loader = f"{self.marshal.config.native_lib}Loader"
            package = '.'.join(self.marshal.config.package + ["native_lib"])
            package_path = Path("/".join(package.split(".")))
            self.write_source(
                template="loader.java.jinja2",
                filename=package_path / f"{loader}.java",
                loader=loader,
                package=package
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_loader()
