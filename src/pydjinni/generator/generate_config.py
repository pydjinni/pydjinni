from pathlib import Path

from pydantic import BaseModel


class GenerateBaseConfig(BaseModel):
    list_out_files: Path = None
    list_in_files: Path = None
