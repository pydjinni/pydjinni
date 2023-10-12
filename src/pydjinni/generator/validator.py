from pydjinni.exceptions import ApplicationException


class LanguageKeywords:
    def __init__(self, language: str, keywords: list[str]):
        self.language = language
        self.keywords = keywords


class InvalidIdentifierException(ApplicationException, code=161):
    """Invalid identifier"""


def validate(language_keywords: LanguageKeywords, separator: str = None):
    def decorator(func):
        def wrapper(self, *args, **kwargs) -> str:
            result: str = func(self, *args, **kwargs)
            tokens = result.split(separator) if separator else [result]
            for token in tokens:
                if token in language_keywords.keywords:
                    raise InvalidIdentifierException(
                        f"The identifier '{token}' is a reserved keyword in {language_keywords.language}",
                        position=self.decl.position
                        )
            return result

        return wrapper

    return decorator
