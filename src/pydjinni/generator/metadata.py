from functools import cached_property

import inspect
from importlib_metadata import version
from pydantic import create_model
from pydantic.fields import FieldInfo
from pydantic import BaseModel, computed_field


class MetadataBase(BaseModel):

    @computed_field
    @cached_property
    def pydjinni_version(self) -> str:
        return version("pydjinni")


class MetadataModelBuilder:
    def __init__(self) -> None:
        self.__fields: dict[str, type[BaseModel]] = {}

    def add_field(self, key: str, model: type[BaseModel]):
        self.__fields[key] = model

    def build(self, config) -> type[MetadataBase]:
        fields_with_fieldinfo = {
            key: (
                model,
                FieldInfo(
                    default=model(config=getattr(config, key)),
                    description=inspect.cleandoc(model.__doc__) if model.__doc__ else None,
                ),
            )
            for key, model in self.__fields.items()
        }

        return create_model(
            "Metadata",
            __base__=MetadataBase,
            **fields_with_fieldinfo,  # type: ignore
        )
