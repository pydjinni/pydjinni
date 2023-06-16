from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.generator.java.java.type import JavaType
from pydjinni.generator.java.jni.config import JniConfig
from pydjinni.generator.java.jni.marshal import JniMarshal
from pydjinni.generator.java.jni.type import JniType, JniField
from pydjinni.parser.ast import Interface
from pydjinni.parser.base_models import BaseType, BaseField
from pydjinni.parser.identifier import Identifier
from pydjinni.parser.type_model_builder import TypeModelBuilder


def given() -> JniMarshal:
    # GIVEN a Marshal instance
    config_model_builder_mock = MagicMock(spec=ConfigModelBuilder)
    type_model_builder_mock = MagicMock(spec=TypeModelBuilder)
    return JniMarshal(
        key="jni",
        config_model_builder=config_model_builder_mock,
        external_type_model_builder=type_model_builder_mock
    )

@pytest.mark.parametrize(
    "config, type_def, translator, header, typename, type_signature, name, jni_prefix, source, namespace",
    [
        (
                JniConfig(out=Path("out/jni")),
                Interface(name=Identifier("foo"), targets=["jni"], comment=["foo"], java=JavaType(
                    boxed="Foo",
                    name="Foo",
                    source=Path(),
                    package="foo.bar"
                )),
                "::Foo", "foo.hpp", "jobject", 'foo/bar/Foo$CppProxy', "Foo", "Java_foo_bar_Foo_00024CppProxy", "foo.cpp", ""
        ),
    ]
)
def test_marshal_type(
        config: JniConfig,
        type_def: BaseType,
        translator: str,
        header: str,
        typename: str,
        type_signature: str,
        name: str,
        jni_prefix: str,
        source: str,
        namespace: str
):
    marshal = given()
    marshal.configure(config)

    # WHEN marshalling a given type
    marshal.marshal_type(type_def)

    # THEN the marshalled type information should be attached to the type_def

    jni_type_def: JniType = type_def.jni
    assert jni_type_def.translator == translator
    assert jni_type_def.header == Path(header)
    assert jni_type_def.typename == typename
    assert jni_type_def.type_signature == type_signature
    assert jni_type_def.name == name
    assert jni_type_def.jni_prefix == jni_prefix
    assert jni_type_def.source == Path(source)
    assert jni_type_def.namespace == namespace



@pytest.mark.parametrize(
    "config, field_def, name, comment",
    [
        (JniConfig(out=Path("out/jni")), Interface.Method(name=Identifier("foo")), "foo", ""),
    ]
)
def test_marshal_field(config: JniConfig, field_def: BaseField, name: str, comment: str):
    marshal = given()
    marshal.configure(config)

    # WHEN marshalling a given field
    marshal.marshal_field(field_def)

    # THEN the marshalled field should be attached to the field_def

    jni_field_def: JniField = field_def.jni
    assert jni_field_def.name == name
