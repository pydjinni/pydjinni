from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.generator.cpp.cpp.config import CppConfig
from pydjinni.generator.cpp.cpp.marshal import CppMarshal
from pydjinni.generator.cpp.cpp.type import CppType, CppField
from pydjinni.parser.ast import Interface, Record
from pydjinni.parser.base_models import BaseType, BaseField, Constant
from pydjinni.parser.identifier import Identifier
from pydjinni.parser.type_model_builder import TypeModelBuilder


def given() -> CppMarshal:
    # GIVEN a Marshal instance
    config_model_builder_mock = MagicMock(spec=ConfigModelBuilder)
    type_model_builder_mock = MagicMock(spec=TypeModelBuilder)
    return CppMarshal(
        key="cpp",
        config_model_builder=config_model_builder_mock,
        external_type_model_builder=type_model_builder_mock
    )

@pytest.mark.parametrize(
    "config, type_def, typename, header, name, source, comment, namespace, proxy",
    [
        (
                CppConfig(out=Path("out/cpp")),
                Interface(name=Identifier("foo"), targets=["cpp"]),
                "::Foo", 'foo.hpp', "Foo", 'foo.cpp', "", "", True
        ),
        (
                CppConfig(out=Path("out/cpp")),
                Interface(name=Identifier("foo")),
                "::Foo", 'foo.hpp', "Foo", 'foo.cpp', "", "", False
        ),
        (
                CppConfig(out=Path("out/cpp"), namespace="foo::bar"),
                Interface(name=Identifier("foo"), targets=["cpp"]),
                "::foo::bar::Foo", 'foo.hpp', "Foo", 'foo.cpp', "", "foo::bar", True
        ),
        (
                CppConfig(out=Path("out/cpp"), namespace="foo::bar"),
                Interface(name=Identifier("foo"), targets=["cpp"], namespace=[Identifier("foobar")]),
                "::foo::bar::foobar::Foo", 'foo.hpp', "Foo", 'foo.cpp', "", "foo::bar::foobar", True
        ),
        (
                CppConfig(out=Path("out/cpp")),
                Interface(name=Identifier("foo"), targets=["cpp"], comment=["foo"]),
                "::Foo", 'foo.hpp', "Foo", 'foo.cpp', "/** foo */", "", True
        ),
        (
                CppConfig(out=Path("out/cpp")),
                Record(name=Identifier("foo")),
                "::Foo", 'foo.hpp', "Foo", 'foo.cpp', "", "", False
        )
    ]
)
def test_marshal_type(
        config: CppConfig,
        type_def: BaseType,
        typename: str,
        header: str,
        name: str,
        source: str,
        comment: str,
        namespace: str,
        proxy: bool):
    marshal = given()
    marshal.configure(config)

    # WHEN marshalling a given type
    marshal.marshal_type(type_def)

    # THEN the marshalled type information should be attached to the type_def

    cpp_type_def: CppType = type_def.cpp
    assert cpp_type_def.typename == typename
    assert cpp_type_def.header == Path(header)
    assert cpp_type_def.by_value == False
    assert cpp_type_def.name == name
    assert cpp_type_def.source == Path(source)
    assert cpp_type_def.comment == comment
    assert cpp_type_def.namespace == namespace
    assert cpp_type_def.proxy == proxy


@pytest.mark.parametrize(
    "config, field_def, name, comment",
    [
        (CppConfig(out=Path("out/cpp")), Interface.Method(name=Identifier("foo")), "foo", ""),
        (CppConfig(out=Path("out/cpp")), Constant(name=Identifier("foo"), value=4), "FOO", ""),
        (CppConfig(out=Path("out/cpp")), Constant(name=Identifier("foo"), value=4, comment=["foo"]), "FOO", "/** foo */"),
    ]
)
def test_marshal_field(config: CppConfig, field_def: BaseField, name: str, comment: str):
    marshal = given()
    marshal.configure(config)

    # WHEN marshalling a given field
    marshal.marshal_field(field_def)

    # THEN the marshalled field should be attached to the field_def

    cpp_field_def: CppField = field_def.cpp
    assert cpp_field_def.name == name
    assert cpp_field_def.comment == comment
