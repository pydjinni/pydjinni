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
