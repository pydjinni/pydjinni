from pathlib import Path

from lsprotocol.types import DocumentSymbol, SymbolKind, DiagnosticSeverity, Diagnostic, Range, Position

from pydjinni import API
from pydjinni.exceptions import ApplicationException
from pydjinni.parser.ast import Namespace, Interface, Record, Enum, Flags, ErrorDomain, Function
from pydjinni.parser.base_models import BaseType, BaseField, TypeReference, SymbolicConstantType


def to_diagnostic(definition: ApplicationException | BaseType | BaseField, severity: DiagnosticSeverity, description: str) -> Diagnostic:
    return Diagnostic(
        range=type_range(definition),
        severity=severity,
        message=description,
        source="pydjinni-language-server"
    )


def to_hover_cache(type_refs: list[TypeReference]) -> dict[int, dict[int, TypeReference]]:
    cache: dict[int, dict[int, TypeReference]] = {}

    def cache_ref(ref: TypeReference):
        for i in range(ref.position.start.col, ref.position.end.col):
            cache[ref.position.start.line][i] = ref
        for parameter_ref in ref.parameters:
            cache_ref(parameter_ref)

    for ref in type_refs:
        if not cache.get(ref.position.start.line):
            cache[ref.position.start.line] = {}

        cache_ref(ref)
    return cache


def type_range(definition: BaseField | BaseType | ApplicationException) -> Range:
    return Range(
        start=Position(definition.position.start.line - 1, definition.position.start.col),
        end=Position(definition.position.end.line - 1, definition.position.end.col)
    )

def configure_api(config: Path) -> API.ConfiguredContext:
    if config.exists():
        return API().configure(path=config)
    else:
        return API().configure(options={ "generate": {} })

def map_kind(type_def):
    if isinstance(type_def, Interface):
        return SymbolKind.Interface
    elif isinstance(type_def, Record) or isinstance(type_def, ErrorDomain):
        return SymbolKind.Struct
    elif isinstance(type_def, Function):
        return SymbolKind.Function
    elif isinstance(type_def, SymbolicConstantType):
        return SymbolKind.Enum
    else:
        return SymbolKind.Null

def to_document_symbol(type_def):
    if isinstance(type_def, Namespace):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Namespace,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            children=[to_document_symbol(child) for child in type_def.children]
        )
    elif isinstance(type_def, Interface):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Interface,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            deprecated=type_def.deprecated != False,
            detail="interface",
            children=[
                DocumentSymbol(
                    name=method.name,
                    kind=SymbolKind.Method,
                    range=type_range(method),
                    selection_range=type_range(method),
                    deprecated=method.deprecated != False,
                    detail=method.return_type_ref.name if method.return_type_ref else None,
                    children=[
                        DocumentSymbol(
                            name=parameter.name,
                            kind=SymbolKind.Variable,
                            range=type_range(parameter),
                            selection_range=type_range(parameter),
                            detail=parameter.type_ref.name
                        )
                        for parameter in method.parameters
                    ]
                ) for method in type_def.methods
            ]
        )
    elif isinstance(type_def, Record):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Class,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            deprecated=type_def.deprecated != False,
            detail="record",
            children=[
                DocumentSymbol(
                    name=field.name,
                    kind=SymbolKind.Field,
                    range=type_range(field),
                    selection_range=type_range(field),
                    detail=field.type_ref.name
                ) for field in type_def.fields
            ]
        )
    elif isinstance(type_def, Enum):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Enum,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            deprecated=type_def.deprecated != False,
            detail="enum",
            children=[
                DocumentSymbol(
                    name=item.name,
                    kind=SymbolKind.EnumMember,
                    range=type_range(item),
                    selection_range=type_range(item)
                ) for item in type_def.items
            ]
        )
    elif isinstance(type_def, Flags):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Enum,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            deprecated=type_def.deprecated != False,
            detail="flags",
            children=[
                DocumentSymbol(
                    name=flag.name,
                    kind=SymbolKind.EnumMember,
                    range=type_range(flag),
                    selection_range=type_range(flag),
                    detail="all" if flag.all else "none" if flag.none else None
                ) for flag in type_def.flags
            ]
        )
    elif isinstance(type_def, ErrorDomain):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Class,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            deprecated=type_def.deprecated != False,
            detail="error",
            children=[
                DocumentSymbol(
                    name=error_code.name,
                    kind=SymbolKind.Field,
                    range=type_range(error_code),
                    selection_range=type_range(error_code),
                    children=[
                        DocumentSymbol(
                            name=parameter.name,
                            kind=SymbolKind.Variable,
                            range=type_range(parameter),
                            selection_range=type_range(parameter),
                            detail=parameter.type_ref.name
                        ) for parameter in error_code.parameters
                    ]
                ) for error_code in type_def.error_codes
            ]
        )
    elif isinstance(type_def, Function):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Function,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            deprecated=type_def.deprecated != False,
            detail=type_def.return_type_ref.name if type_def.return_type_ref else None,
            children=[
                DocumentSymbol(
                    name=parameter.name,
                    kind=SymbolKind.Variable,
                    range=type_range(parameter),
                    selection_range=type_range(parameter),
                    detail=parameter.type_ref.name
                )
                for parameter in type_def.parameters
            ]
        )
    else:
        return DocumentSymbol(
            name=type_def.name,
            kind=map_kind(type_def),
            range=type_range(type_def),
            selection_range=type_range(type_def)
        )
