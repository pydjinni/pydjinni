# Copyright 2023 jothepro
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
import re
from abc import ABC, abstractmethod
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from pydjinni.documentation.html_renderer import HTMLRenderer
from pydjinni.exceptions import ApplicationException
from pydjinni.parser.base_models import BaseType, BaseExternalType, BaseCommentModel


class DocumentationGenerator(ABC):
    class DocumentationGenerationException(ApplicationException, code=190):
        """Documentation Generation error"""

        def __init__(self, input_def: BaseType, message: str):
            super().__init__(message)
            self.input_def = input_def

    @property
    @abstractmethod
    def key(self) -> str:
        """
        The name of the documentation plugin. Will be used as configuration key.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def __init__(self):
        self._generator_directory = Path(inspect.getfile(self.__class__)).parent

        def comment(decl: BaseCommentModel):
            return HTMLRenderer().render_tokens(*decl.parsed_comment) if decl.comment else ""


        self._jinja_env = Environment(
            loader=FileSystemLoader(self._generator_directory / "templates"),
            trim_blocks=True, lstrip_blocks=True,
            keep_trailing_newline=True
        )
        self._jinja_env.filters["comment"] = comment

    def template(self, template: str, **attrs):
        return self._jinja_env.get_template(template).render(
            **attrs
        )

    def generate(self, decl: BaseType) -> tuple[str, str]:
        def call_generate_method(definition: BaseType):
            def traverse_hierarchy(def_class, definition):
                if def_class == BaseExternalType:
                    raise DocumentationGenerator.DocumentationGenerationException(
                        definition,
                        f"The documentation generator '{self.key}' does not support the type '{definition.__class__.__qualname__}'"
                    )
                qualifier = '_'.join(
                    [word.lower() for word in re.findall(r'[A-Z][a-z0-9]*', def_class.__qualname__)])
                method_name = f"generate_{qualifier}"
                if hasattr(self, method_name):
                    return getattr(self, method_name)(definition)
                else:
                    for base in def_class.__bases__:
                        traverse_hierarchy(base, definition)

            return traverse_hierarchy(definition.__class__, definition)

        return call_generate_method(decl)
