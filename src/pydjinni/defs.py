from pathlib import Path
import pkg_resources

DEFAULT_CONFIG_PATH = Path("pydjinni.yaml")
IDL_GRAMMAR_PATH = Path(pkg_resources.resource_filename(__name__, "parser/grammar/idl.cleanpeg"))
