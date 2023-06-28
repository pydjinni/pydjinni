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
        self.write_header(
            template="header/enum.hpp.jinja2",
            path=self.marshal.header_path() / type_def.jni.header,
            type_def=type_def
        )

    def generate_flags(self, type_def: Flags):
        self.write_header(
            template="header/flags.hpp.jinja2",
            path=self.marshal.header_path() / type_def.jni.header,
            type_def=type_def
        )

    def generate_record(self, type_def: Record):
        self.write_header(
            template="header/record.hpp",
            path=self.marshal.header_path() / type_def.jni.header,
            type_def=type_def
        )
        self.write_source(
            template="source/record.cpp",
            path=self.marshal.source_path() / type_def.jni.source,
            type_def=type_def
        )

    def generate_interface(self, type_def: Interface):
        self.write_header(
            template="header/interface.hpp",
            path=self.marshal.header_path() / type_def.jni.header,
            type_def=type_def
        )
        self.write_source(
            template="source/interface.cpp",
            path=self.marshal.source_path() / type_def.jni.source,
            type_def=type_def
        )

    def generate_loader(self):
        if self.marshal.config.loader:
            self.write_source(
                template="source/loader.cpp.jinja2",
                path=self.marshal.source_path() / "pydjinni" / "jni" / "loader.cpp"
            )

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        super().generate(ast, copy_support_lib_sources)
        self.generate_loader()
