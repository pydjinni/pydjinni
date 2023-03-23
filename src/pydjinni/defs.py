from pathlib import Path
import pkg_resources

DEFAULT_CONFIG_PATH = Path("pydjinni.yaml")
IDL_GRAMMAR_PATH = Path(pkg_resources.resource_filename(__name__, "res/grammar/idl.cleanpeg"))
TYPES_DIR = Path(pkg_resources.resource_filename(__name__, "res/types/"))
TEMPLATES_DIR = Path(pkg_resources.resource_filename(__name__, "res/templates/"))
