import pytest

from pydjinni.parser.model.elements import Enum, Flags, Interface, Primitive, Record, TypeReference
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.namespace_tuple import NamespaceTuple
from pydjinni.parser.providers.type_registry import TypeRegistry


@pytest.fixture
def registry() -> TypeRegistry:
    return TypeRegistry()


@pytest.mark.parametrize(
    "definition_namespace",
    (
        NamespaceTuple((Identifier("foo"), Identifier("bar"))),
        NamespaceTuple((Identifier("foo"),)),
        NamespaceTuple(),
    ),
)
def test_type_registry_resolve_relative_reference_searches_namespace_prefixes(
    registry: TypeRegistry,
    definition_namespace: NamespaceTuple,
):
    # GIVEN a type registered in the current namespace or one of its parents
    definition = Enum(
        name=Identifier("baz"),
        namespace=definition_namespace,
    )
    registry.register(definition)

    # AND GIVEN a TypeReference that references the type
    reference = TypeReference(
        name=Identifier("baz"),
        namespace=NamespaceTuple((Identifier("foo"), Identifier("bar"))),
        parameters=(),
    )

    # WHEN resolving the relative reference
    resolved = registry.resolve(reference)

    # THEN the registered definition should be returned
    assert resolved is definition


def test_type_registry_resolve_relative_reference_prefers_nearest_namespace(registry: TypeRegistry):
    # GIVEN a type with the same name registered in the current namespace and its parent
    current_definition = Flags(
        name=Identifier("baz"),
        namespace=NamespaceTuple((Identifier("foo"), Identifier("bar"))),
    )
    parent_definition = Flags(
        name=Identifier("baz"),
        namespace=NamespaceTuple((Identifier("foo"),)),
    )
    registry.register(parent_definition)
    registry.register(current_definition)

    # AND GIVEN a TypeReference that references the type
    reference = TypeReference(
        name=Identifier("baz"),
        namespace=NamespaceTuple((Identifier("foo"), Identifier("bar"))),
        parameters=(),
    )

    # WHEN resolving the relative reference
    resolved = registry.resolve(reference)

    # THEN the definition in the current namespace should be returned
    assert resolved is current_definition


def test_type_registry_resolve_absolute_reference(registry: TypeRegistry):
    # GIVEN a type registered in a namespace
    definition = Primitive(
        name=Identifier("baz"),
        namespace=NamespaceTuple((Identifier("foo"), Identifier("bar"))),
    )
    registry.register(definition)

    # AND GIVEN an absolute reference to it
    reference = TypeReference(
        name=Identifier("baz"),
        namespace_prefix=NamespaceTuple((Identifier("foo"), Identifier("bar"))),
        absolute=True,
        namespace=NamespaceTuple((Identifier("other"),)),
        parameters=(),
    )

    # WHEN resolving the absolute reference
    resolved = registry.resolve(reference)

    # THEN the namespace on the reference should not affect the result
    assert resolved is definition


@pytest.mark.parametrize(
    "reference",
    (
        TypeReference(
            name=Identifier("missing"),
            namespace=NamespaceTuple((Identifier("foo"),)),
            parameters=(),
        ),
        TypeReference(
            name=Identifier("missing"),
            namespace_prefix=NamespaceTuple((Identifier("foo"),)),
            absolute=True,
            parameters=(),
        ),
    ),
)
def test_type_registry_resolve_unknown_reference_raises(registry: TypeRegistry, reference: TypeReference):
    # GIVEN an empty registry
    # WHEN resolving an unknown reference
    # THEN the exception should retain the reference that failed to resolve
    with pytest.raises(TypeRegistry.TypeResolvingException, check=lambda e: e.reference is reference):
        registry.resolve(reference)


def test_type_registry_successful_type_registration(registry: TypeRegistry):
    # GIVEN a type and an empty registry
    definition = Interface(name=Identifier("baz"))

    # WHEN registering and resolving the type
    registry.register(definition)
    resolved = registry.resolve(
        TypeReference(
            name=Identifier("baz"),
            parameters=(),
        ),
    )

    # THEN the registered type should be returned
    assert resolved is definition


def test_type_registry_register_duplicate_type_raises(registry: TypeRegistry):
    # GIVEN a type already registered
    existing_definition = Record(name=Identifier("baz"))
    registry.register(existing_definition)

    # WHEN registering another type with the same key
    new_definition = Record(name=Identifier("baz"))
    with pytest.raises(TypeRegistry.DuplicateTypeException) as exception:
        registry.register(new_definition)

    # THEN the exception should contain both definitions
    assert exception.value.new_type is new_definition
    assert exception.value.existing_type is existing_definition
