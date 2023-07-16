from .yaml.generator import YamlGenerator
from pydjinni.generator.target import Target


class YamlTarget(Target):
    """
    Generate YAML type interfaces.
    """
    key = "yaml"
    generators = [YamlGenerator]
