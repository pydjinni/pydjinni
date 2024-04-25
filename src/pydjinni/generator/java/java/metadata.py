from functools import cached_property

from pydantic import BaseModel, Field, computed_field

from .config import JavaConfig


class JavaMetadata(BaseModel):
    """
    Java Generator Metadata
    """
    config: JavaConfig = Field(exclude=True, repr=False)

    @computed_field
    @cached_property
    def base_package(self) -> str: return '.'.join(self.config.package)
