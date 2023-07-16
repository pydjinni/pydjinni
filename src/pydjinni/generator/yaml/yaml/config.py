from pathlib import Path

from pydantic import BaseModel, Field


class YamlConfig(BaseModel):
    """
    When generating the interface for your project and wish to make it available to other users
    you can tell Djinni to generate a special YAML file as part of the code generation process.
    This file then contains all the information Djinni requires to include your types in a different project.
    """
    out: Path = Field(
        description="The output folder for YAML files (One for each type by default)."
    )
    out_file: Path = Field(
        default=None,
        description="If specified, all types are merged into a single YAML file "
                    "instead of generating one file per type (relative to `yaml.out`)."
    )
