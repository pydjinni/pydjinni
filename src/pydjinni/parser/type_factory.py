from __future__ import annotations

from pydantic import create_model, Field
from pydantic.fields import FieldInfo, Undefined

from pydjinni.generator.generator import Generator, Target


class TypeFactory:
    """
    Create the BaseModel for (external) type validation from all loaded generator modules
    """

    def __init__(self):
        self._generators: list[Generator] = []

    def add_generator(self, generator: Generator) -> TypeFactory:
        self._generators.append(generator)
        return self

    def add_target(self, target: Target) -> TypeFactory:
        for generator in target.generators:
            self.add_generator(generator)
        return self

    def build(self):
        field_kwargs = {_generator.key: (_generator.type_config, None) for _generator in self._generators if _generator.type_config is not None}
        return create_model(
            "Type",
            name=(str,Field(
                description="The name of the type in the interface definition"
            )),
            comment=(str | None, Field(
                default=None,
                description="A comment describing the type"
            )),
            **field_kwargs
        )
