from pydantic import BaseModel

from pydjinni.parser.base_models import BaseExternalType


class ExternalTypesBuilder:
    external_types: dict[str, BaseExternalType] = {
        "bool": BaseExternalType(
            name='bool',
            primitive=BaseExternalType.Primitive.bool,
            comment="boolean type"
        ),
        "i8": BaseExternalType(
            name='i8',
            primitive=BaseExternalType.Primitive.int,
            comment="8 bit integer type"
        ),
        "i16": BaseExternalType(
            name='i16',
            primitive=BaseExternalType.Primitive.int,
            comment="16 bit integer type"
        ),
        "i32": BaseExternalType(
            name='i32',
            primitive=BaseExternalType.Primitive.int,
            comment="32 bit integer type"
        ),
        "i64": BaseExternalType(
            name='i64',
            primitive=BaseExternalType.Primitive.int,
            comment="64 bit integer type"
        ),
        "f32": BaseExternalType(
            name='f32',
            primitive=BaseExternalType.Primitive.float,
            comment="float type"
        ),
        "f64": BaseExternalType(
            name='f64',
            primitive=BaseExternalType.Primitive.double,
            comment="double type"
        ),
        "string": BaseExternalType(
            name='string',
            primitive=BaseExternalType.Primitive.string,
            comment="string"
        ),
        "binary": BaseExternalType(
            name='binary',
            comment="binary data"
        ),
        "list": BaseExternalType(
            name='list',
            comment="a list of items of type T",
            params=["T"]

        ),
        "set": BaseExternalType(
            name='set',
            comment="a set of unique items of type T",
            params=["T"]

        ),
        "map": BaseExternalType(
            name='map',
            comment="a map of key-value pairs of type K, V",
            params=["K", "V"]
        )
    }

    def __init__(self, external_base_type: type[BaseModel]):
        self._external_base_type = external_base_type
        self._external_types: dict[str, dict] = {}

    def register(self, key: str, external_types: dict):
        self._external_types[key] = external_types

    def build(self) -> list:
        output = []
        for field, model in self.external_types.items():
            field_kwargs = {key: external_types[field] for key, external_types in self._external_types.items() if external_types.get(field)}
            output.append(self._external_base_type(
                name=model.name,
                primitive=model.primitive,
                comment=model.comment,
                params=model.params,
                **field_kwargs
            ))
        return output
