from typing import Annotated, Final, cast
lazy from collections.abc import Iterator
lazy from pathlib import Path
lazy from types import UnionType

from pydantic import Discriminator, RootModel, ValidationError
from yaml import MarkedYAMLError, Node, SafeLoader

from pydjinni.exceptions import FileNotFoundException, InputParsingException
from pydjinni.position import Cursor, Position
lazy from pydjinni.parser.model.elements import Type


class YamlTypeParser:
    def __init__(self, type_models: UnionType) -> None:
        self._type_models: Final = type_models

    def parse(self, path: Path) -> Iterator[Type]:
        """Parses type definitions from a YAML file.

        Raises:
            FileNotFoundException: If ``path`` does not exist.
            InputParsingException: If the YAML is malformed or a parsed document does not match a type model.
        """
        root_model: Final = RootModel[Annotated[self._type_models, Discriminator("kind")]]

        try:
            with path.open() as file:
                loader: Final = SafeLoader(file)
                try:
                    loader.check_node()
                    while document_node := loader.get_node():
                        try:
                            if isinstance(type_dict := loader.construct_document(document_node), dict):
                                type_dict["position"] = self._get_position(path, document_node)
                            yield cast("Type", root_model.model_validate(type_dict).root)
                        except ValidationError as e:
                            raise InputParsingException.from_pydantic_error(e, file=path)
                except MarkedYAMLError as e:
                    raise InputParsingException.from_yaml_error(e)
                finally:
                    loader.dispose()
        except FileNotFoundError:
            raise FileNotFoundException(path)

    def _get_position(self, path: Path, document_node: Node) -> Position:
        return Position(
            file=path,
            start=Cursor(line=document_node.start_mark.line, col=document_node.start_mark.column),
            end=Cursor(line=document_node.end_mark.line, col=document_node.end_mark.column),
        )
