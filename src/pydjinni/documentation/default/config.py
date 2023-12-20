from pathlib import Path

from pydantic import BaseModel, Field


class DefaultDocumentationConfig(BaseModel):
    """
    HTML configuration options
    """

    out: Path = Field(
        description="The output folder for the generated HTML files."
    )

    title: str = Field(
        description="Title of the website."
    )

    description: str = Field(
        description="Short project description"
    )

    logo: Path = Field(
        default=None,
        description="Path to a logo of the documentation website"
    )

    home: Path = Field(
        description="Path to a Markdown file that should be used as home page."
    )

    docs: dict[str, Path] = Field(
        default=[],
        description="A list of additional Markdown documents that should be added to the documentation"
    )

    default_language: str = Field(
        description="The target language that should be selected by default"
    )
