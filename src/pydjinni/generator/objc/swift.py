from pydantic import BaseModel, Field

from pydjinni.generator.generator import HeaderOnlyBaseConfig


class SwiftConfig(HeaderOnlyBaseConfig):
    bridging_header: str = Field(
        description="The name of Objective-C Bridging Header used in XCode's Swift projects."
    )

class SwiftType(BaseModel):
    typename: str

    @classmethod
    def from_name(cls, name: str):
        return cls(
            typename=name.lower()
        )
