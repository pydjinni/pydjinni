
return_codes: dict[int, str] = {}


class ApplicationException(Exception):
    """Pydjinni Application Exception"""

    def __init_subclass__(cls, code: int = -1):
        if code > 0:
            cls.code = code
            assert return_codes.get(code) is None, f"The return code '{code}' is already in use!"
            return_codes[code] = cls.__doc__

    def __init__(self, description: str):
        self.description = description

    def __str__(self) -> str:
        return f"{self.__doc__}: {self.description}"
