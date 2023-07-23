from pathlib import Path

import pytest
import yaml

from pydjinni.exceptions import InputParsingException
from pydjinni.parser.ast import TypeReference
from pydjinni.parser.base_models import BaseType, BaseExternalType
from pydjinni.parser.resolver import Resolver


def internal_given() -> tuple[Resolver, BaseType, TypeReference]:
    # GIVEN a resolver instance
    resolver = Resolver(BaseExternalType)

    # AND GIVEN a type that should be registered
    new_type = BaseType(name="foo", namespace=[])

    # AND GIVEN a type reference to the same type
    type_ref = TypeReference(name="foo", parameters=[], namespace=[])

    return resolver, new_type, type_ref


def external_given() -> tuple[Resolver, BaseExternalType, TypeReference]:
    # GIVEN a resolver instance
    resolver = Resolver(BaseExternalType)

    # AND GIVEN a type that should be registered
    new_type = BaseExternalType(name="foo", primitive='record', namespace=[])

    # AND GIVEN a type reference to the same type
    type_ref = TypeReference(name="foo", parameters=[], namespace=[])

    return resolver, new_type, type_ref


def test_register_type():
    resolver, new_type, type_ref = internal_given()

    # WHEN registering the new type
    resolver.register(new_type)

    # AND WHEN resolving the registered type from a provided type reference
    type_def = resolver.resolve(type_ref)

    # THEN the type_ref should now contain a reference to the new type
    assert type_def == new_type


def test_register_type_twice():
    resolver, new_type, type_ref = internal_given()

    # WHEN registering the new type
    resolver.register(new_type)

    # AND WHEN registering the new type again
    # THEN a DuplicateTypeException should be raised
    with pytest.raises(Resolver.TypeResolvingException, match="Type 'foo' already exists"):
        resolver.register(new_type)


def test_resolve_unknown_type():
    resolver, new_type, type_ref = internal_given()

    # WHEN resolving the type reference without registering the new type before
    # THEN a TypeResolvingException should be raised
    with pytest.raises(Resolver.TypeResolvingException):
        resolver.resolve(type_ref)


def test_register_external_type():
    resolver, new_external_type, type_ref = external_given()

    # WHEN registering the new external type
    resolver.register_external(new_external_type)

    # AND WHEN resolving the registered type from a provided type reference
    type_def = resolver.resolve(type_ref)

    # THEN the type_ref should now contain a reference to the new type
    assert type_def == new_external_type


def test_load_external_type(tmp_path: Path):
    # GIVEN an external type model
    class ExternalType(BaseExternalType):
        foo: int

    # AND GIVEN a Resolver instance
    resolver = Resolver(ExternalType)

    # AND GIVEN an input file with an external type definition
    file = tmp_path / "my_type.yaml"
    file.write_text(yaml.dump({
        'name': 'bar',
        'primitive': 'record',
        'foo': 5
    }))

    # AND GIVEN a type reference to the external type
    type_ref = TypeReference(name="bar", parameters=[], namespace=[])

    # WHEN loading the type definition from the file
    resolver.load_external(file)

    # AND WHEN resolving the type
    type_def = resolver.resolve(type_ref)

    # THEN the type reference should contain a reference to the external type
    assert type_def.name == "bar"
    assert type_def.foo == 5
    assert type_def.primitive == BaseExternalType.Primitive.record


def test_load_invalid_external_type(tmp_path: Path):
    # GIVEN a Resolver instance
    resolver = Resolver(BaseExternalType)

    # AND GIVEN an input file with an invalid external type definition
    file = tmp_path / "my_type.yaml"
    file.write_text(yaml.dump({
        'name': 5  # int is not the expected type for the field 'name'
    }))

    # AND GIVEN a type reference to the external type
    TypeReference(name="bar", parameters=[])

    # WHEN loading the type definition from the file
    # THEN an InputParsingException should be raised
    with pytest.raises(InputParsingException):
        resolver.load_external(file)


@pytest.mark.parametrize("type_ref,type_def,wrong_type_def", [
    (TypeReference(name="foo.bar"), BaseType(name="bar", namespace="foo"), None),
    (TypeReference(name="foo.bar", namespace="foo"), BaseType(name="bar", namespace="foo"), None),
    (TypeReference(name="bar", namespace="foo"), BaseType(name="bar"), None),
    (TypeReference(name=".bar", namespace="foo"), BaseType(name="bar"), BaseType(name="bar", namespace="foo"))
])
def test_register_namespaced_type(tmp_path: Path, type_ref: TypeReference, type_def: BaseType, wrong_type_def: BaseType):
    # GIVEN a resolver instance
    resolver = Resolver(BaseExternalType)

    # WHEN registering the new type
    resolver.register(type_def)
    # AND WHEN (optionally) registering a wrong type that we are not looking for
    if wrong_type_def:
        resolver.register(wrong_type_def)

    # AND WHEN resolving the registered type from a provided type reference
    resolved_type_def = resolver.resolve(type_ref)

    # THEN the type_ref should now contain a reference to the new type
    assert resolved_type_def == type_def
