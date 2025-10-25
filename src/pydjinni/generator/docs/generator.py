# Copyright 2025 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
from pathlib import Path
import re
import shutil
from typing import Generic, TypeVar, get_args
from attr import dataclass
from pygments.lexers import get_lexer_by_name
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from pygments.formatters import HtmlFormatter
from pygments import highlight
from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.exceptions import ApplicationException, ConfigurationException
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.generator.docs.registry import DocumentationTargetRegistry
from pydjinni.parser.ast import Namespace
from .comment_renderer import DocumentationCommentRenderer
from pydjinni.parser.base_models import BaseCommentModel, BaseExternalType, BaseType

ConfigModel = TypeVar("ConfigModel", bound=BaseModel)


class DocumentationGenerator(Generic[ConfigModel]):
    key: str
    display_key: str
    marshal_models: dict[type, type] = {}
    lexer_language: str

    __config_model: type
    """
    Pydantic model specifying the documentation target configuration
    """

    def __init_subclass__(cls) -> None:
        generic_types = get_args(cls.__orig_bases__[0])  # type: ignore
        assert (
            len(generic_types) > 0
        ), "A DocumentationGenerator implementation must at least specify a config model as generic parameter"
        cls.__config_model = generic_types[0]

    class DocumentationGenerationException(ApplicationException, code=190):
        """Generation error"""

        def __init__(self, input_def: BaseType, message: str):
            super().__init__(message)
            self.input_def = input_def

    def __init__(
        self,
        file_writer: FileReaderWriter,
        config_model_builder: ConfigModelBuilder,
        documentation_target_registry: DocumentationTargetRegistry,
    ) -> None:
        self.config: ConfigModel | None
        self._file_writer = file_writer
        self._generator_directory = Path(inspect.getfile(self.__class__)).parent
        self._parent_generator_directory = Path(inspect.getfile(DocumentationGenerator)).parent
        self._comment_renderer = DocumentationCommentRenderer()
        self._code_lexer = get_lexer_by_name(self.lexer_language)
        self._code_formatter = HtmlFormatter()
        self._documentation_target_registry = documentation_target_registry

        config_model_builder.add_documentation_config(self.key, self.__config_model)

        self._jinja_env = Environment(
            loader=FileSystemLoader(
                [self._parent_generator_directory / "templates", self._generator_directory / "templates"]
            ),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            extensions=['jinja2.ext.do']
        )

        def highlight_filter(code: str) -> str:
            return highlight(code, self._code_lexer, self._code_formatter)

        def comment_filter(comment_type: BaseCommentModel) -> str:
            if comment_type._parsed_comment:
                return self._comment_renderer.render_tokens(*comment_type._parsed_comment)
            else:
                return ""

        self._jinja_env.filters["comment"] = comment_filter
        self._jinja_env.filters["highlight"] = highlight_filter
        self._jinja_env.globals.update(isinstance=isinstance)

    @property
    def docs_path(self) -> Path:
        return self.documentation_root / self.key

    @property
    def documentation_target(self) -> DocumentationTargetRegistry.DocumentationTarget:
        return DocumentationTargetRegistry.DocumentationTarget(self.key, self.display_key)

    @property
    def styles_path(self) -> Path:
        return self.documentation_root / "styles"

    def configure(
        self,
        config: ConfigModel,
        documentation_root: Path,
        title: str,
    ):
        self.documentation_root = documentation_root
        self.config = config
        self.title = title
        if config:
            self._documentation_target_registry.register(self.documentation_target)
            

    def _assert_config_exists(self):
        if not hasattr(self, "config") or self.config is None:
            raise ConfigurationException(f"Missing configuration for 'documentation.{self.key}'!")

    def clean(self):
        """purge all content from documentation output directory"""
        shutil.rmtree(self.docs_path, ignore_errors=True)

    def _generate_stylesheets(self):
        self.styles_path.mkdir(exist_ok=True, parents=True)
        (self.styles_path / "highlight.css").write_text(self._code_formatter.get_style_defs(".highlight"))
        shutil.copy(self._parent_generator_directory / "styles" / "style.css", self.styles_path / "style.css")

    def generate(self, ast: list[BaseType | Namespace], targets: list[DocumentationTargetRegistry.DocumentationTarget]):
        self._ast = ast
        self.targets = targets

        def call_generate_method(definition: BaseType | Namespace):
            def traverse_hierarchy(def_class, definition):
                if def_class == BaseExternalType:
                    raise DocumentationGenerator.DocumentationGenerationException(
                        definition,
                        f"The generator '{self.key}' does not support the type '{definition.__class__.__qualname__}'",
                    )
                qualifier = "_".join([word.lower() for word in re.findall(r"[A-Z][a-z0-9]*", def_class.__qualname__)])
                method_name = f"generate_{qualifier}"
                if hasattr(self, method_name):
                    getattr(self, method_name)(definition)
                else:
                    for base in def_class.__bases__:
                        traverse_hierarchy(base, definition)

            traverse_hierarchy(definition.__class__, definition)

        if self.config:
            self._generate_stylesheets()
            self.docs_path.mkdir(exist_ok=True, parents=True)
            for type_def in ast:
                call_generate_method(type_def)

    def write_docs(
        self,
        template: Path,
        type_def: BaseExternalType | Namespace | None = None,
        filename: Path | None = None,
        **kwargs,
    ):
        if type_def is not None and filename is None:
            filename = Path(f"{"_".join(([] if isinstance(type_def, Namespace) else type_def.namespace) + [type_def.name])}.html")
        assert filename, "If no type_def is given, an explicit filename must be provided"
        self._jinja_env.get_template(template.as_posix()).stream(
            type_def=type_def,
            all_type_defs=self._ast,
            title=self.title,
            filename=filename,
            targets=self.targets,
            key=self.key,
            **kwargs,
        ).dump((self.docs_path / filename).as_posix())
