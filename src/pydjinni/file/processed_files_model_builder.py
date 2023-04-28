from pathlib import Path

from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo


class ProcessedFiles(BaseModel):
    class ParsedFiles(BaseModel):
        """List of input files that have been parsed. This does not include the config file."""
        idl: list[Path] = Field(
            default=[]
        )
        external_types: list[Path] = Field(
            default=[]
        )

    parsed: ParsedFiles = ParsedFiles()


class ProcessedFilesModelBuilder:
    def __init__(self):
        self._generated_fields: dict[str, tuple[bool, bool]] = {}

    def add_generated_field(self, key: str, header: bool = True, source: bool = True):
        self._generated_fields[key] = (header, source)

    def build(self):
        generated_files_model = self._generated_files_model()
        generated_files_model.__doc__ = "List of generated files from all registered generators"
        return create_model(
            "ProcessedFiles",
            __base__=ProcessedFiles,
            generated=(generated_files_model, generated_files_model())
        )

    def _generated_files_model(self):
        def key_model(key: str, fields: tuple[bool, bool]):
            fields_kwargs = {}
            if fields[0]:
                fields_kwargs["header"] = (list[Path], FieldInfo(
                    default=[],
                    description=f"List of generated {key} header files."
                ))
            if fields[1]:
                fields_kwargs["source"] = (list[Path], FieldInfo(
                    default=[],
                    description=f"List of generated {key} source files."
                ))
            return create_model(
                f"Generated_{key}",
                **fields_kwargs
            )
        field_kwargs = {}
        for key, fields in self._generated_fields.items():
            model = key_model(key, fields)
            field_kwargs[key] = (model, model())
        return create_model(
            "Generated",
            **field_kwargs
        )

