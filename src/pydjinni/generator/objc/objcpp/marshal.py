from pydjinni.generator.marshal import Marshal
from pydjinni.parser.base_models import BaseField, BaseType
from .config import ObjcppConfig
from .external_types import external_types
from .type import ObjcppExternalType


class ObjcppMarshal(Marshal[ObjcppConfig, ObjcppExternalType], types=external_types):
    def marshal_type(self, type_def: BaseType):
        pass

    def marshal_field(self, field_def: BaseField):
        pass
