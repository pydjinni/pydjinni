# Copyright 2023 jothepro
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

from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from pydjinni.generator.objc.objc.comment_renderer import DocCCommentRenderer
from pydjinni.generator.objc.objc.config import ObjcConfig
from pydjinni.generator.objc.objc.keywords import swift_keywords, keywords
from pydjinni.generator.validator import validate
from pydjinni.parser.ast import Record, Interface, Parameter, Function
from pydjinni.parser.base_models import BaseType, BaseExternalType, BaseField, TypeReference
from pydjinni.parser.identifier import IdentifierType as Identifier


class ObjcExternalType(BaseModel):
    typename: str = None
    boxed: str
    header: Path = None
    pointer: bool = True


def type_decl(type_ref: TypeReference, parameter: bool = False, boxed: bool = False) -> str:
    type_def: BaseExternalType | BaseType = type_ref.type_def
    generic_types = ""
    pointer = type_def.objc.pointer
    optional = type_ref.optional
    typename = type_def.objc.boxed if boxed or optional else type_def.objc.typename
    if type_ref.parameters:
        generic_types = "<"
        for parameter_ref in type_ref.parameters:
            if len(generic_types) > 1:
                generic_types += ", "
            generic_types += type_decl(parameter_ref, boxed=True)
        generic_types += ">"
    if type_def.primitive == BaseExternalType.Primitive.interface:
        if parameter:
            typename = f"id<{typename}>"
            pointer = False

    return f"{typename}{generic_types}{' *' if pointer or boxed or optional else ''}"


def annotation(type_ref: TypeReference):
    if type_ref and ((isinstance(type_ref.type_def, Interface) or
                      (isinstance(type_ref.type_def, BaseExternalType) and
                       type_ref.type_def.primitive == BaseExternalType.Primitive.interface)) or
                     type_ref.optional):
        return "nullable"
    elif type_ref and type_ref.type_def.objc.pointer:
        return "nonnull"
    else:
        return ""


class ObjcBaseType(BaseModel):
    decl: BaseType = Field(exclude=True, repr=False)
    config: ObjcConfig = Field(exclude=True, repr=False)

    @cached_property
    @validate(keywords)
    def name(self) -> str:
        return f"{self.config.type_prefix}{self.namespace}{self.decl.name.convert(self.config.identifier.type)}"

    @computed_field
    @cached_property
    def typename(self) -> str:
        return f"{self.config.type_prefix}{self.namespace}{self.decl.name.convert(self.config.identifier.type)}"

    @computed_field
    @cached_property
    def boxed(self) -> str: return self.typename

    @computed_field
    @cached_property
    def header(self) -> Path: return Path(f"{self.name}.{self.config.header_extension}")

    @cached_property
    def source(self) -> Path: return Path(f"{self.name}.{self.config.source_extension}")

    @computed_field
    @cached_property
    def pointer(self) -> bool: return False

    @cached_property
    @validate(swift_keywords)
    def swift_typename(self) -> str:
        return f"{self.namespace}.{self.name}" if self.namespace else self.name

    @cached_property
    def comment(self):
        return DocCCommentRenderer(self.config.identifier).render_tokens(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''

    @cached_property
    def namespace(self): return '.'.join([identifier.convert(self.config.identifier.type)
                                          for identifier in self.decl.namespace])


class ObjcFunction(ObjcBaseType):
    decl: Function = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def typename(self) -> str:
        return_type_decl = type_decl(self.decl.return_type_ref) if self.decl.return_type_ref else "void"
        parameter_type_decls = [type_decl(parameter.type_ref, parameter=True) for parameter in self.decl.parameters]
        return f"{return_type_decl} (^)({', '.join(parameter_type_decls)})"

    @computed_field
    @cached_property
    def header(self) -> Path: return None


class ObjcBaseClassType(ObjcBaseType):
    @computed_field
    @cached_property
    def pointer(self) -> bool: return True


class ObjcBaseField(BaseModel):
    decl: BaseField = Field(exclude=True, repr=False)
    config: ObjcConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    @validate(keywords)
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.field)

    @cached_property
    def comment(self):
        return DocCCommentRenderer(self.config.identifier).render_tokens(*self.decl.parsed_comment).strip() \
            if self.decl.comment else ''


class ObjcRecord(ObjcBaseClassType):
    decl: Record = Field(exclude=True, repr=False)

    @cached_property
    @validate(keywords)
    def name(self) -> str:
        if self.base_type:
            return f"{self.config.type_prefix}{self.namespace}{Identifier(f'{self.decl.name}_base').convert(self.config.identifier.type)}"
        else:
            return super().typename

    @cached_property
    def derived_name(self) -> str:
        return f"{self.config.type_prefix}{self.namespace}{self.decl.name.convert(self.config.identifier.type)}"

    @cached_property
    def derived_header(self) -> Path:
        return Path(f"{self.derived_name}.{self.config.header_extension}")

    @cached_property
    def base_type(self) -> bool:
        return "objc" in self.decl.targets

    @cached_property
    def init(self) -> str:
        return Identifier(f"init_with_{self.decl.fields[0].name}").convert(self.config.identifier.method) \
            if self.decl.fields else "init"

    @cached_property
    def convenience_init(self) -> str:
        name = f"{self.decl.name}_base" if self.base_type else self.decl.name
        return Identifier(f"{name}_with_{self.decl.fields[0].name}").convert(self.config.identifier.method) \
            if self.decl.fields else self.decl.name.convert(self.config.identifier.method)

    class ObjcField(ObjcBaseField):
        @cached_property
        def type_decl(self) -> str:
            return type_decl(self.decl.type_ref)

        @cached_property
        def annotation(self) -> str:
            return annotation(self.decl.type_ref)

        @cached_property
        def hash_code(self) -> str:
            if self.decl.type_ref.type_def.primitive in [
                BaseExternalType.Primitive.enum,
                BaseExternalType.Primitive.flags
            ]:
                return f"(NSUInteger)self.{self.decl.objc.name}"
            elif self.decl.type_ref.optional or self.decl.type_ref.type_def.objc.typename == self.decl.type_ref.type_def.objc.boxed:
                return f"self.{self.decl.objc.name}.hash"
            else:
                return f"(NSUInteger)self.{self.decl.objc.name}"

        @cached_property
        def equals(self) -> str:
            if self.decl.type_ref.type_def.primitive in [
                BaseExternalType.Primitive.enum,
                BaseExternalType.Primitive.flags
            ]:
                return f"self.{self.decl.objc.name} == typedOther.{self.decl.objc.name}"
            elif self.decl.type_ref.optional:
                return f"((self.{self.decl.objc.name} == nil && typedOther.{self.decl.objc.name} == nil) || (self.{self.decl.objc.name} != nil && [self.{self.decl.objc.name} isEqual:typedOther.{self.decl.objc.name}]))"
            elif self.decl.type_ref.type_def.objc.typename == self.decl.type_ref.type_def.objc.boxed:
                match self.decl.type_ref.type_def.name:
                    case 'binary':
                        return f"[self.{self.decl.objc.name} isEqualToData:typedOther.{self.decl.objc.name}]"
                    case 'list':
                        return f"[self.{self.decl.objc.name} isEqualToArray:typedOther.{self.decl.objc.name}]"
                    case 'set':
                        return f"[self.{self.decl.objc.name} isEqualToSet:typedOther.{self.decl.objc.name}]"
                    case 'map':
                        return f"[self.{self.decl.objc.name} isEqualToDictionary:typedOther.{self.decl.objc.name}]"
                    case 'string':
                        return f"[self.{self.decl.objc.name} isEqualToString:typedOther.{self.decl.objc.name}]"
                    case 'date':
                        return f"[self.{self.decl.objc.name} isEqualToDate:typedOther.{self.decl.objc.name}]"
                    case _:
                        return f"[self.{self.decl.objc.name} isEqual:typedOther.{self.decl.objc.name}]"
            else:
                return f"self.{self.decl.objc.name} == typedOther.{self.decl.objc.name}"


class ObjcParameter(ObjcBaseField):
    decl: Parameter = Field(exclude=True, repr=False)

    @cached_property
    def type_decl(self) -> str: return type_decl(self.decl.type_ref, parameter=True)

    @cached_property
    def annotation(self) -> str: return annotation(self.decl.type_ref)


class ObjcSymbolicConstantField(ObjcBaseField):
    @computed_field
    @cached_property
    @validate(keywords)
    def name(self) -> str: return self.decl.name.convert(self.config.identifier.enum)


class ObjcInterface(ObjcBaseClassType):
    class ObjcMethod(ObjcBaseField):
        decl: Interface.Method = Field(exclude=True, repr=False)

        @computed_field
        @cached_property
        @validate(keywords)
        def name(self) -> str: return self.decl.name.convert(self.config.identifier.method)

        @cached_property
        def type_decl(self) -> str: return type_decl(self.decl.return_type_ref) if self.decl.return_type_ref else "void"

        @cached_property
        def specifier(self) -> str: return "+" if self.decl.static else "-"

        @cached_property
        def annotation(self) -> str: return annotation(self.decl.return_type_ref)
