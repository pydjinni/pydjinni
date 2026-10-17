from unittest.mock import Mock

import pytest

from pydjinni.parser.providers.type_registry import TypeRegistry


@pytest.fixture
def type_registry_mock() -> Mock:
    return Mock(TypeRegistry)
