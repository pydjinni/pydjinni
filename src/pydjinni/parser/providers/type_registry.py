from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

lazy from pydjinni.parser.model.namespace_tuple import NamespaceTuple

if TYPE_CHECKING:
    from pydjinni.parser.model.elements import Type, TypeReference


class TypeRegistry:
    @dataclass(frozen=True)
    class TypeResolvingException(Exception):
        reference: TypeReference

    @dataclass(frozen=True)
    class DuplicateTypeException(Exception):
        new_type: Type
        existing_type: Type

    def __init__(self) -> None:
        self._registry: Final[dict[str, Type]] = {}
        self._usage_tracker: Final[set[str]] = set()

    def register(self, new_type: Type) -> None:
        """
        Registers a new type in the type registry.

        Raises:
            DuplicateTypeException: when a type with the same identifier already exists
        """
        if existing_type := self._registry.get(new_type.key):
            raise self.DuplicateTypeException(
                new_type=new_type,
                existing_type=existing_type,
            )

        self._registry[new_type.key] = new_type

    def resolve(self, reference: TypeReference) -> Type:
        """
        resolves a given ``TypeReference`` to the registered ``Type``

        Raises:
            TypeResolvingException: when the type cannot be resolved

        Returns:
            Type: If the ``TypeReference`` could be resolved
        """
        if reference.absolute:
            definition = self._resolve_absolute_reference(reference.key)
        else:
            definition = self._resolve_relative_reference(reference.namespace, reference.key)

        if definition is None:
            raise self.TypeResolvingException(reference=reference)

        self._usage_tracker.add(definition.key)
        return definition

    def _resolve_absolute_reference(self, key: str) -> Type | None:
        return self._registry.get(key)

    def _resolve_relative_reference(self, namespace: NamespaceTuple, key: str) -> Type | None:
        namespace_segments = [identifier.value for identifier in namespace.values]
        for end in range(len(namespace_segments), -1, -1):
            if definition := self._registry.get("." + ".".join((*namespace_segments[:end], key))):
                return definition
        return None
