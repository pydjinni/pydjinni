from pathlib import Path

return_codes: dict[int, str] = {}


class ApplicationException(Exception):
    """Pydjinni Application Exception"""

    def __init_subclass__(cls, code: int = -1):
        cls.code = code
        assert return_codes.get(code) is None, f"The return code '{code}' is already in use!"
        return_codes[code] = cls.__doc__

    def __init__(self, param: str, file: Path = None):
        self._param = param
        self._file = file

    def __str__(self) -> str:
        return f"{self.__doc__}{f' in {self._file.absolute()}' if self._file is not None else ''}: {self._param}"


class FileNotFoundException(ApplicationException, code=2):
    """The file could not be found"""

    def __init__(self, file: Path):
        super().__init__(str(file.absolute()))


class InputParsingException(ApplicationException, code=140):
    """Parsing input has failed"""


class ConfigurationException(InputParsingException, code=141):
    """Error loading the configuration"""
