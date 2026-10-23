import json
import shutil
import tomllib
from enum import StrEnum
from typing import Any, Final, NamedTuple
lazy from collections.abc import Iterable
lazy from pathlib import Path

import json5
import tomli_w
import yaml
from pydash import merge
lazy from pydantic import BaseModel, ValidationError

from pydjinni.exceptions import FileNotFoundException, InputParsingException
from pydjinni.position import Position


class FileHandler:
    """Common utility class for reading and writing files in PyDjinni."""

    class ReadResult[T](NamedTuple):
        """Result of a file read operation."""

        file: Path
        content: T

    class FileExtensions(StrEnum):
        """Enum of all supported input/output Pydantic model file types."""

        yaml = ".yaml"
        yml = ".yml"
        json = ".json"
        json5 = ".json5"
        toml = ".toml"

    def __init__(self, root: Path) -> None:
        if root.is_file():
            raise ValueError(f"root path must be a directory: {root}")
        self._root: Final = root

    def read(self, file: Path) -> ReadResult[str]:
        """Read the file content from a relative or absolute file.

        Args:
            file: a relative or absolute input path. For relative paths, the configured root path is prepended.

        Returns:
            ReadResult: the resolved file path that was used to read the input, and the content of the file.

        Raises:
            FileNotFoundException: if the requested file does not exist.
        """
        resolved_file_path: Final = self._root / file
        try:
            return self.ReadResult(
                file=resolved_file_path,
                content=resolved_file_path.read_text(),
            )
        except FileNotFoundError:
            raise FileNotFoundException(resolved_file_path)

    def write(self, file: Path, content: str) -> Path:
        """Write content to a relative or absolute file.

        Args:
            file: a relative or absolute output path. For relative paths, the configured root path is prepended.
            content: the content to be written.

        Returns:
            Path: the resolved file path that was used to write the output.
        """
        resolved_file_path: Final = self._root / file
        resolved_file_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_file_path.write_text(content)
        return resolved_file_path

    def write_model(self, file: Path, model: BaseModel) -> Path:
        """Write a Pydantic model in a variety of output file formats.

        The output format is determined by the file suffix.
        Supported values are:

        - `.yaml`, `.yml`
        - `.json`, `.json5`
        - `.toml`

        Returns:
            Path: the resolved file path that was used to write the output.

        Raises:
            ValueError: if the file suffix is not supported
        """
        model_dump = model.model_dump(mode="json")
        match file.suffix:
            case self.FileExtensions.yaml | self.FileExtensions.yml:
                content = yaml.dump(model_dump)
            case self.FileExtensions.json:
                content = json.dumps(model_dump, indent=2)
            case self.FileExtensions.json5:
                content = json5.dumps(model_dump, indent=2)
            case self.FileExtensions.toml:
                content = tomli_w.dumps(model_dump)
            case _:
                raise ValueError(f"Unknown model dump file extension: '{file.suffix}'")
        return self.write(file, content)

    def read_model[T: BaseModel](
        self,
        file: Path,
        model_type: type[T],
        additional_input_dict: frozendict[str, Any] = frozendict(),
    ) -> ReadResult[T]:
        """Read an input file into a Pydantic model.

        The input format is determined by the file suffix.
        Supported values are:

        - `.yaml`, `.yml`
        - `.json`, `.json5`
        - `.toml`

        Args:
            file: a relative or absolute input path. For relative paths, the configured root path is prepended.
            model_type: the model that the input should be serialized into.
            additional_input_dict: additional input data that should be merged with the contents of the file.
                                   Properties from this dict will override keys from the input file.

        Returns:
            ReadResult: the resolved file path that was used to read the input, and the parsed Pydantic model.

        Raises:
            InputParsingException: if the input cannot be parsed.
        """  # ruff: ignore[docstring-missing-exception]
        resolved_file, content = self.read(file)
        match resolved_file.suffix:
            case self.FileExtensions.yaml | self.FileExtensions.yml:
                try:
                    input_dict = yaml.safe_load(content)
                except yaml.MarkedYAMLError as e:
                    raise InputParsingException.from_yaml_error(e)
            case self.FileExtensions.json:
                try:
                    input_dict = json.loads(content)
                except json.JSONDecodeError as e:
                    raise InputParsingException.from_json_error(resolved_file, e)
            case self.FileExtensions.json5:
                try:
                    input_dict = json5.loads(content)
                except ValueError as e:
                    raise InputParsingException(
                        description=f"json5 parsing error {e}",
                        position=Position.from_file(resolved_file),
                    )
            case self.FileExtensions.toml:
                try:
                    input_dict = tomllib.loads(content)
                except tomllib.TOMLDecodeError as e:
                    raise InputParsingException.from_toml_error(resolved_file, e)
            case _:
                raise InputParsingException(f"Unknown input file extension: '{resolved_file.suffix}'")

        try:
            return self.ReadResult(
                file=resolved_file,
                content=model_type.model_validate(
                    merge(input_dict, additional_input_dict),
                ),
            )
        except ValidationError as e:
            raise InputParsingException.from_pydantic_error(resolved_file, e)

    def copy(self, source: Path, destination: Path) -> Path:
        """Copy a file to a given destination.

        The destination must be a file path including the target filename.
        Intermediate directories are created if not yet present.

        Args:
            source: the file to copy
            destination: the file destination. Must include the file name.

        Returns:
            the path of the destination file
        """
        resolved_source_file_path: Final = self._root / source
        resolved_destination_file_path: Final = self._root / destination
        resolved_destination_file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        return Path(
            shutil.copy(
                src=resolved_source_file_path,
                dst=resolved_destination_file_path,
            )
        )

    def copy_directory(self, source: Path, destination: Path) -> Iterable[Path]:
        """Copy all files from a directory and it's subdirectories.

        Args:
            source: the source directory
            destination: the destination directory

        Yields:
            Path: the paths of all copied files.
        """
        resolved_source = self._root / source
        for dirpath, _, filenames in resolved_source.walk():
            for name in filenames:
                yield self.copy(
                    source=dirpath / name,
                    destination=destination / dirpath.relative_to(resolved_source) / name,
                )
