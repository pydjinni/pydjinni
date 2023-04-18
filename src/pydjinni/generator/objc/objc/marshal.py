from pydjinni.generator.marshal import Marshal
from pydjinni.parser.base_models import BaseField, BaseType
from .external_types import external_types
from .type import ObjcExternalType
from .config import ObjcConfig


class ObjcMarshal(Marshal[ObjcConfig, ObjcExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        pass

    def marshal_field(self, field_def: BaseField):
        pass
