from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.generator.java.java.config import JavaConfig
from pydjinni.generator.java.java.marshal import JavaMarshal
from pydjinni.generator.java.java.type import JavaType, JavaField
from pydjinni.parser.ast import Interface
from pydjinni.parser.base_models import BaseType, BaseField, Constant
from pydjinni.parser.identifier import Identifier
from pydjinni.parser.type_model_builder import TypeModelBuilder


def given() -> JavaMarshal:
    # GIVEN a Marshal instance
    config_model_builder_mock = MagicMock(spec=ConfigModelBuilder)
    type_model_builder_mock = MagicMock(spec=TypeModelBuilder)
    return JavaMarshal(
        key="java",
        config_model_builder=config_model_builder_mock,
        external_type_model_builder=type_model_builder_mock
    )

@pytest.mark.parametrize(
    "config, type_def, typename, boxed, name, source, package, comment",
    [
        (
                JavaConfig(out=Path("out/java")),
                Interface(name=Identifier("foo"), targets=["java"], comment=["foo"]),
                "Foo", "Foo", "Foo", 'Foo.java', "", "/** foo */"
        ),
        (
                JavaConfig(out=Path("out/java"), package="foo.bar"),
                Interface(name=Identifier("foo"), targets=["java"]),
                "foo.bar.Foo", "foo.bar.Foo", "Foo", 'foo/bar/Foo.java', "foo.bar", ""
        ),
        (
                JavaConfig(out=Path("out/java"), package="foo.bar"),
                Interface(name=Identifier("foo"), targets=["java"], namespace=[Identifier("foobar")]),
                "foo.bar.foobar.Foo", "foo.bar.foobar.Foo", "Foo", 'foo/bar/foobar/Foo.java', "foo.bar.foobar", ""
        ),
    ]
)
def test_marshal_type(
        config: JavaConfig,
        type_def: BaseType,
        typename: str,
        boxed: str,
        name: str,
        source: str,
        package: str,
        comment: str
):
    marshal = given()
    marshal.configure(config)

    # WHEN marshalling a given type
    marshal.marshal_type(type_def)

    # THEN the marshalled type information should be attached to the type_def

    java_type_def: JavaType = type_def.java
    assert java_type_def.typename == typename
    assert java_type_def.boxed == boxed
    assert java_type_def.name == name
    assert java_type_def.source == Path(source)
    assert java_type_def.package == package
    assert java_type_def.comment == comment


@pytest.mark.parametrize(
    "config, field_def, name, comment",
    [
        (JavaConfig(out=Path("out/java")), Interface.Method(name=Identifier("foo")), "foo", ""),
        (JavaConfig(out=Path("out/java")), Constant(name=Identifier("foo")), "FOO", ""),
    ]
)
def test_marshal_field(config: JavaConfig, field_def: BaseField, name: str, comment: str):
    marshal = given()
    marshal.configure(config)

    # WHEN marshalling a given field
    marshal.marshal_field(field_def)

    # THEN the marshalled field should be attached to the field_def

    java_field_def: JavaField = field_def.java
    assert java_field_def.name == name
    assert java_field_def.comment == comment
