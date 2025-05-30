# Copyright 2025 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lsprotocol.types import (
    DocumentSymbol,
    SymbolKind,
    DiagnosticSeverity,
    Diagnostic,
    Range,
    Position,
    CompletionItemKind,
)

from pydjinni.position import Position as PyDjinniPosition
from pydjinni.exceptions import ApplicationException
from pydjinni.parser.ast import Namespace, Interface, Record, Enum, Flags, ErrorDomain, Function
from pydjinni.parser.base_models import (
    BaseExternalType,
    BaseType,
    BaseField,
    TypeReference,
    SymbolicConstantType,
    FileReference,
)
from pydjinni_language_server.models import Diagnostics


def to_diagnostic(
    definition: ApplicationException | BaseType | BaseField, severity: DiagnosticSeverity, description: str
) -> Diagnostic:
    return Diagnostic(
        range=type_range(definition), severity=severity, message=description, source="pydjinni-language-server"
    )


def to_diagnostics(diagnostics: Diagnostics):
    error_diagnostics = [
        Diagnostic(range=type_range(error.definition), severity=DiagnosticSeverity.Error, message=error.message)
        for error in diagnostics.errors
    ]
    warning_diagnostics = [
        Diagnostic(range=type_range(warning.definition), severity=DiagnosticSeverity.Warning, message=warning.message)
        for warning in diagnostics.warnings
    ]
    return error_diagnostics + warning_diagnostics


def to_hover_cache(
    items: list[TypeReference | FileReference | BaseField | Namespace | BaseType],
) -> dict[int, dict[int, TypeReference | FileReference | BaseField | Namespace | BaseType]]:
    cache: dict[int, dict[int, TypeReference | FileReference | BaseField | Namespace | BaseType]] = {}

    def cache_ref(ref: TypeReference | FileReference | BaseField | Namespace | BaseType):
        if ref.identifier_position and ref.identifier_position.start:
            if not cache.get(ref.identifier_position.start.line):
                cache[ref.identifier_position.start.line] = {}
            for i in range(ref.identifier_position.start.col, ref.identifier_position.end.col):
                cache[ref.identifier_position.start.line][i] = ref
            if isinstance(ref, TypeReference):
                for parameter_ref in ref.parameters:
                    cache_ref(parameter_ref)
            elif isinstance(ref, Namespace):
                for child in ref.children:
                    cache_ref(child)

    for ref in items:
        cache_ref(ref)
    return cache


def type_range(definition: BaseField | BaseExternalType | Namespace | TypeReference | ApplicationException) -> Range:
    if definition.position and definition.position.start and definition.position.end:
        return Range(
            start=Position(definition.position.start.line, definition.position.start.col),
            end=Position(definition.position.end.line, definition.position.end.col),
        )
    else:
        return Range(start=Position(0, 0), end=Position(0, 0))


def identifier_range(definition: TypeReference | FileReference | BaseField | Namespace | BaseType) -> Range:
    if definition.identifier_position and definition.identifier_position.start and definition.identifier_position.end:
        return Range(
            start=Position(definition.identifier_position.start.line, definition.identifier_position.start.col),
            end=Position(definition.identifier_position.end.line, definition.identifier_position.end.col),
        )
    else:
        return Range(start=Position(0, 0), end=Position(0, 0))


def to_range(position: PyDjinniPosition):
    return Range(
        start=Position(position.start.line, position.start.col), end=Position(position.end.line, position.end.col)
    )


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


def map_completion_item_kind(type_def: BaseExternalType) -> CompletionItemKind | None:
    match type_def.primitive:
        case BaseExternalType.Primitive.interface:
            return CompletionItemKind.Interface
        case BaseExternalType.Primitive.record | BaseExternalType.Primitive.error:
            return CompletionItemKind.Struct
        case BaseExternalType.Primitive.function:
            return CompletionItemKind.Function
        case BaseExternalType.Primitive.enum | BaseExternalType.Primitive.flags:
            return CompletionItemKind.Enum
        case BaseExternalType.Primitive.collection:
            return CompletionItemKind.Class
        case _:
            return CompletionItemKind.Value


def to_document_symbol(type_def) -> DocumentSymbol:
    if isinstance(type_def, Namespace):
        return DocumentSymbol(
            name=type_def.name,
            kind=SymbolKind.Namespace,
            range=type_range(type_def),
            selection_range=type_range(type_def),
            children=[to_document_symbol(child) for child in type_def.children],
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
                            detail=parameter.type_ref.name,
                        )
                        for parameter in method.parameters
                    ],
                )
                for method in type_def.methods
            ],
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
                    detail=field.type_ref.name,
                )
                for field in type_def.fields
            ],
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
                    name=item.name, kind=SymbolKind.EnumMember, range=type_range(item), selection_range=type_range(item)
                )
                for item in type_def.items
            ],
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
                    detail="all" if flag.all else "none" if flag.none else None,
                )
                for flag in type_def.flags
            ],
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
                            detail=parameter.type_ref.name,
                        )
                        for parameter in error_code.parameters
                    ],
                )
                for error_code in type_def.error_codes
            ],
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
                    detail=parameter.type_ref.name,
                )
                for parameter in type_def.parameters
            ],
        )
    else:
        return DocumentSymbol(
            name=type_def.name,
            kind=map_kind(type_def),
            range=type_range(type_def),
            selection_range=type_range(type_def),
        )
