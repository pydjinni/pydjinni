import yaml

from pydjinni.exceptions import ConfigurationException
from pydjinni.generator.generator import Generator
from .config import YamlConfig
from pydjinni.parser.base_models import BaseType, BaseExternalType, BaseField


class YamlGenerator(Generator):

    key = "yaml"
    config_model = YamlConfig
    writes_source = True

    def generate_type_dict(self, type_def: BaseType) -> dict:
        return type_def.model_dump(mode='json', exclude_none=True, exclude=set(
            [field for field in type_def.model_fields.keys() if field not in (BaseExternalType.model_fields.keys())]))

    def generate(self, ast: list[BaseType], copy_support_lib_sources: bool = True):
        filtered_type_defs = [type_def for type_def in ast if not (type_def.primitive == BaseExternalType.Primitive.function and type_def.anonymous)]
        if self.config:
            if self.config.out_file:
                self._file_writer.write_source(
                    key=self.key,
                    filename=self.source_path / self.config.out_file,
                    content=yaml.dump_all([self.generate_type_dict(type_def) for type_def in filtered_type_defs])
                )
            else:
                for type_def in filtered_type_defs:
                    self._file_writer.write_source(
                        key=self.key,
                        filename=self.source_path / f"{type_def.name}.yaml",
                        content=yaml.dump(self.generate_type_dict(type_def))
                    )
        else:
            raise ConfigurationException(f"Missing configuration for 'generator.{self.key}'!")
