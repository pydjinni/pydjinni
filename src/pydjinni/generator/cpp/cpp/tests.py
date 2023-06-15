from pydjinni.parser.ast import Interface
from pydjinni.parser.base_models import BaseExternalType, BaseType


def shared_ptr(type_def: BaseExternalType | BaseType) -> bool:
    return (isinstance(type_def, BaseExternalType) and type_def.primitive == BaseExternalType.Primitive.interface) or \
        type(type_def) is Interface
