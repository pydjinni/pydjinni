from pathlib import PurePosixPath
from pydantic import BaseModel, Field, computed_field

from .config import KotlinConfig
from pydjinni.parser.base_models import BaseExternalType, BaseField, BaseType


class KotlinExternalType(BaseModel):
    """Java type information"""

    typename: str


class KotlinBaseType(BaseModel):
    config: KotlinConfig = Field(exclude=True, repr=False)
    decl: BaseType = Field(exclude=True, repr=False)

    @computed_field
    @property
    def typename(self) -> str:
        return f"{self.package}.{self.decl.java.name}"

    @property
    def package(self) -> str:
        return self.decl.java.package

    @property
    def source(self):
        return PurePosixPath(*self.package.split(".")) / f"{self.decl.java.name}.kt"


class KotlinInterface(KotlinBaseType):
    @property
    def package(self) -> str:
        return f"{self.decl.java.package}.kotlin"


class KotlinBaseField(BaseModel):
    config: KotlinConfig = Field(exclude=True, repr=False)
    decl: BaseField = Field(exclude=True, repr=False)

    @property
    def data_type(self) -> str:
        result = self.decl.type_ref.type_def.kotlin.typename
        if self.decl.type_ref.optional:
            result += "?"
        return result

    @property
    def java_delegate_data_type(self) -> str:
        if self.decl.type_ref.type_def.primitive == BaseExternalType.Primitive.interface:
            result = self.decl.type_ref.type_def.java.typename
        else:
            result = self.decl.type_ref.type_def.kotlin.typename
        if self.decl.type_ref.optional:
            result += "?"
        return result

    @property
    def return_type(self) -> str:
        if self.decl.return_type_ref:
            result = self.decl.return_type_ref.type_def.kotlin.typename
            if self.decl.return_type_ref.optional:
                result += "?"
        else:
            result = "Unit"
        return result

    @property
    def java_delegate_raw_return_type(self) -> str:
        if self.decl.return_type_ref:
            if self.decl.return_type_ref.type_def.primitive == BaseExternalType.Primitive.interface:
                result = self.decl.return_type_ref.type_def.java.typename
            else:
                result = self.decl.return_type_ref.type_def.kotlin.typename
            if self.decl.return_type_ref.optional:
                result += "?"
        else:
            result = "Unit"
        return result

    @property
    def java_delegate_return_type(self) -> str:
        result = self.java_delegate_raw_return_type
        if self.decl.asynchronous:
            if not self.decl.return_type_ref:
                result = "Void"
            result = f"java.util.concurrent.CompletableFuture<{result}>"

        return result
