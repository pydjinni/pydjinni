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

import shutil
from pathlib import Path

import mistune

from pydjinni.documentation.default.config import DefaultDocumentationConfig
from pydjinni.documentation.generator import DocumentationGenerator
from pydjinni.documentation.target import DocumentationTarget
from pydjinni.parser.base_models import BaseType


class DefaultDocumentationTarget(DocumentationTarget):
    key = "default"
    config_model = DefaultDocumentationConfig

    def file_output_path(self, generator: DocumentationGenerator, decl: BaseType) -> Path:
        return Path(self.config.out) / generator.key / Path(*decl.namespace) / f"{decl.name}.html"

    def generate_nav_tree(self, generator: DocumentationGenerator, ast: list[BaseType]) -> dict[str, Path | dict]:
        result: dict[str, Path | dict] = {}
        for decl in ast:
            insert_position: dict = result
            for namespace in decl.namespace:
                if namespace not in insert_position:
                    insert_position[namespace] = {}
                insert_position = insert_position[namespace]
            name, content = generator.generate(decl)
            insert_position[name] = generator.key / Path(*decl.namespace) / f"{decl.name}.html"
        return result

    def generate(self, ast: list[BaseType], clean: bool = False):
        self._jinja_env.filters['file_output_path'] = self.file_output_path
        super().generate(ast, clean)
        self.write_file(
            file=self.config.out / "index.html",
            template="index.jinja2",
            name="Redirect"
        )
        shutil.copy(self._generator_directory / "templates" / "style.css", self.config.out)
        shutil.copy(self.config.logo, self.config.out)

        for generator in self.generators:
            for decl in ast:
                name, content = generator.generate(decl)
                self.write_file(
                    file=self.file_output_path(generator, decl),
                    template="template.jinja2",
                    generators=self.generators,
                    current_generator=generator,
                    relative_path=Path(*decl.namespace) / f"{decl.name}.html",
                    content=content,
                    name=name,
                    deprecated=mistune.html(decl.deprecated) if isinstance(decl.deprecated, str) else decl.deprecated,
                    decl=decl,
                    logo=self.config.logo.name,
                    tree=self.generate_nav_tree(generator, ast)
                )

            self.write_file(
                file=self.config.out / generator.key / "index.html",
                template="template.jinja2",
                generators=self.generators,
                current_generator=generator,
                relative_path="index.html",
                content=mistune.html(self.config.home.read_text()),
                name="Home",
                logo=self.config.logo.name,
                tree=self.generate_nav_tree(generator, ast)
            )
            for title, doc in self.config.docs.items():
                self.write_file(
                    file=self.config.out / generator.key / f"{title.lower()}.html",
                    template="template.jinja2",
                    generators=self.generators,
                    current_generator=generator,
                    relative_path=f"{title.lower()}.html",
                    content=mistune.html(doc.read_text()),
                    name=title,
                    logo=self.config.logo.name,
                    tree=self.generate_nav_tree(generator, ast)
                )
