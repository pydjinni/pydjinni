from pathlib import Path

from pydjinni.generator.filters import quote, headers
from pydjinni.generator.generator import Generator
from pydjinni.parser.ast import Enum, Flags, Record, Interface
from pydjinni.parser.base_models import BaseType
from .marshal import JniMarshal


class JniGenerator(
    Generator,
    key="jni",
    marshal=JniMarshal,
    writes_header=True,
    writes_source=True,
    support_lib_commons=True,
    filters=[quote, headers]
):

    def generate_enum(self, type_def: Enum):
        self.write_header("header/enum.hpp.jinja2", type_def=type_def)

    def generate_flags(self, type_def: Flags):
        self.write_header("header/flags.hpp.jinja2", type_def=type_def)

    def generate_record(self, type_def: Record):
        self.write_header("header/record.hpp", type_def=type_def)
        self.write_source("source/record.cpp", type_def=type_def)

    def generate_interface(self, type_def: Interface):
        self.write_header("header/interface.hpp", type_def=type_def)
        self.write_source("source/interface.cpp", type_def=type_def)

    def generate_loader(self):
        if self.marshal.config.loader:
            self.write_source(
                template="source/loader.cpp.jinja2",
                filename=Path("pydjinni") / "jni" / "loader.cpp"
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_loader()
