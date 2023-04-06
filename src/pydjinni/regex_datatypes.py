import re
from typing import Any

from pydantic_core import core_schema


class CustomRegexType(str):
    pattern: str
    error_message: str
    examples: list[str] = None

    @classmethod
    def __pydantic_modify_json_schema__(cls, field_schema: dict[str, Any]) -> dict[str, Any]:
        field_schema.update(pattern=cls.pattern)
        if cls.examples is not None:
            field_schema.update(examples=cls.examples)
        return field_schema

    @classmethod
    def __get_pydantic_core_schema__(
            cls, **_kwargs: Any
    ) -> core_schema.AfterValidatorFunctionSchema:
        return core_schema.general_after_validator_function(
            cls.validate,
            core_schema.str_schema(
                pattern=cls.pattern
            ),
        )

    @classmethod
    def validate(cls, value, _: core_schema.ValidationInfo):
        if not isinstance(value, str):
            raise TypeError('string required')
        regex = re.compile(cls.pattern)
        m = regex.fullmatch(value)
        if not m:
            raise ValueError(f"'{value}' {cls.error_message}")
        return value

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'
