from typing import Annotated

from pydantic import AfterValidator, PlainSerializer, WithJsonSchema

from pydjinni.parser.identifier import Identifier

Namespace = Annotated[
    str,
    AfterValidator(lambda x: [Identifier(i) for i in x.split('.')]),
    PlainSerializer(lambda x: '.'.join(x), return_type=str),
    WithJsonSchema({'type': 'string', 'pattern': r"[_\.\w]+"}, mode='validation')
]
