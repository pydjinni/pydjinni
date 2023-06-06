from pydjinni.parser.base_models import BaseType, BaseExternalType


def type_decl(type_def: BaseType|BaseExternalType) -> str:
    if isinstance(type_def, BaseType) or (isinstance(type_def, BaseExternalType) and not type_def.primitive):
        return f"(nonnull {type_def.objc.typename} *)"
    else:
        return f"({type_def.objc.typename})"
