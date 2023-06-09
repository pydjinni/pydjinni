from pathlib import Path

import pytest
import yaml

from pydjinni.exceptions import InputParsingException
from pydjinni.parser.ast import TypeReference
from pydjinni.parser.base_models import BaseType, BaseExternalType
from pydjinni.parser.identifier import Identifier
from pydjinni.parser.resolver import Resolver


def internal_given() -> tuple[Resolver, BaseType, TypeReference]:
    # GIVEN a resolver instance
    resolver = Resolver(BaseExternalType)

    # AND GIVEN a type that should be registered
    new_type = BaseType(name=Identifier("foo"), position=0)

    # AND GIVEN a type reference to the same type
    type_ref = TypeReference(name=Identifier("foo"), position=2, parameters=[])

    return resolver, new_type, type_ref


def external_given() -> tuple[Resolver, BaseExternalType, TypeReference]:
    # GIVEN a resolver instance
    resolver = Resolver(BaseExternalType)

    # AND GIVEN a type that should be registered
    new_type = BaseExternalType(name="foo")

    # AND GIVEN a type reference to the same type
    type_ref = TypeReference(name=Identifier("foo"), position=2, parameters=[])

    return resolver, new_type, type_ref


def test_register_type():
    resolver, new_type, type_ref = internal_given()

    # WHEN registering the new type
    resolver.register(new_type)

    # AND WHEN resolving the registered type from a provided type reference
    resolver.resolve(type_ref)

    # THEN the type_ref should now contain a reference to the new type
    assert type_ref.type_def == new_type


def test_register_type_twice():
    resolver, new_type, type_ref = internal_given()

    # WHEN registering the new type
    resolver.register(new_type)

    # AND WHEN registering the new type again
    # THEN a DuplicateTypeException should be raised
    with pytest.raises(Resolver.DuplicateTypeException):
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
    resolver.resolve(type_ref)

    # THEN the type_ref should now contain a reference to the new type
    assert type_ref.type_def == new_external_type


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
        'foo': 5
    }))

    # AND GIVEN a type reference to the external type
    type_ref = TypeReference(name=Identifier("bar"), position=2, parameters=[])

    # WHEN loading the type definition from the file
    resolver.load_external(file)

    # AND WHEN resolving the type
    resolver.resolve(type_ref)

    # THEN the type reference should contain a reference to the external type
    assert type_ref.type_def
    assert type_ref.type_def.name == "bar"
    assert type_ref.type_def.foo == 5


def test_load_invalid_external_type(tmp_path: Path):
    # GIVEN a Resolver instance
    resolver = Resolver(BaseExternalType)

    # AND GIVEN an input file with an invalid external type definition
    file = tmp_path / "my_type.yaml"
    file.write_text(yaml.dump({
        'name': 5  # int is not the expected type for the field 'name'
    }))

    # AND GIVEN a type reference to the external type
    TypeReference(name=Identifier("bar"), position=2, parameters=[])

    # WHEN loading the type definition from the file
    # THEN an InputParsingException should be raised
    with pytest.raises(InputParsingException):
        resolver.load_external(file)


def test_register_namespaced_type(tmp_path: Path):
    # GIVEN a resolver instance
    resolver = Resolver(BaseExternalType)

    # AND GIVEN a type with a namespace that should be registered
    new_type = BaseType(name=Identifier("bar"), namespace=[Identifier("foo")], position=0)

    # AND GIVEN a type reference to the same type
    type_ref = TypeReference(name=Identifier("foo.bar"), position=2, parameters=[])

    # WHEN registering the new type
    resolver.register(new_type)

    # AND WHEN resolving the registered type from a provided type reference
    resolver.resolve(type_ref)

    # THEN the type_ref should now contain a reference to the new type
    assert type_ref.type_def == new_type
