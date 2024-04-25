from functools import cached_property

from importlib_metadata import version
from pydantic import BaseModel, computed_field


class MetadataBase(BaseModel):

    @computed_field
    @cached_property
    def pydjinni_version(self) -> str: return version('pydjinni')
