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

from abc import ABC, abstractmethod

from pydjinni.config.config_model_builder import ConfigModelBuilder
from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder
from pydjinni.parser.ast import Record
from pydjinni.parser.base_models import BaseType, BaseField
from pydjinni.parser.type_model_builder import TypeModelBuilder
from .external_types import ExternalTypesBuilder
from .generator import Generator, ConfigModel


class Target(ABC):
    """
    Abstract class for defining generation targets. A target combines multiple generators to one entity.
    E.g. to allow Java interop, both a Java and JNI generator are required.
    """

    @property
    def supported_deriving(self) -> set[Record.Deriving]:
        """
        Record derivings that are supported by the target language.
        For documentation purposes only.
        """
        return set()

    @property
    @abstractmethod
    def key(self) -> str:
        """
        The name of the target. Will be used by the API/CLI for selecting the target.
        """
        pass

    @property
    @abstractmethod
    def generators(self) -> list[type[Generator]]:
        """
        A list of generators related to the target.
        Typically, targets will have two generators:

        1. For the target (host) language
        2. For the glue-code required in C++ to interact with the host language
        """
        pass

    def __init__(
            self,
            file_reader_writer: FileReaderWriter,
            config_model_builder: ConfigModelBuilder,
            external_type_model_builder: TypeModelBuilder,
            processed_files_model_builder: ProcessedFilesModelBuilder):
        self.generator_instances = [generator(
            file_writer=file_reader_writer,
            config_model_builder=config_model_builder,
            external_type_model_builder=external_type_model_builder,
            processed_files_model_builder=processed_files_model_builder
        ) for generator in self.generators]

    def generate(self, ast: list[BaseType], clean: bool = False, copy_support_lib_sources: bool = True):
        for generator_instance in self.generator_instances:
            if clean:
                generator_instance.clean()
            generator_instance.generate(ast, copy_support_lib_sources)

    def marshal(self, type_defs: list[BaseType], field_defs: list[BaseField]):
        for generator in self.generator_instances:
            generator.marshal(type_defs, field_defs)

    def register_external_types(self, external_types_factory: ExternalTypesBuilder):
        for generator in self.generator_instances:
            generator.register_external_types(external_types_factory)

    def configure(self, config: ConfigModel):
        for generator in self.generator_instances:
            generator.configure(getattr(config, generator.key))
