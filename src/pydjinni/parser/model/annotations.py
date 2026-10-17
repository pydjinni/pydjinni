from typing import Annotated

from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

type Internal[T] = Annotated[
    
    SkipJsonSchema[T],
    Field(exclude=True, frozen=True),
    ...,
]
"Marks internal model fields that should not be serialized or included in JSON Schema."
