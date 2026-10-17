import pytest

from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.model.namespace_tuple import NamespaceTuple
from pydjinni.parser.providers.namespace_stack import NamespaceStackProvider


@pytest.fixture
def stack():
    return NamespaceStackProvider()


def test_push_one_namespace(stack: NamespaceStackProvider):
    stack.push(NamespaceTuple((Identifier("foo"),)))


def test_push_multiple_namespaces(stack: NamespaceStackProvider):
    stack.push(NamespaceTuple((Identifier("foo"), Identifier("bar"))))

    assert stack.current == NamespaceTuple((Identifier("foo"), Identifier("bar")))

    stack.pop()

    assert stack.current == NamespaceTuple()


def test_multiple_pushes(stack: NamespaceStackProvider):
    stack.push(NamespaceTuple((Identifier("foo"),)))

    assert stack.current == NamespaceTuple((Identifier("foo"),))

    stack.push(NamespaceTuple((Identifier("bar"), Identifier("baz"))))

    assert stack.current == NamespaceTuple((Identifier("foo"), Identifier("bar"), Identifier("baz")))

    stack.pop()

    assert stack.current == NamespaceTuple((Identifier("foo"),))

    stack.pop()

    assert stack.current == NamespaceTuple()


def test_get_empty(stack: NamespaceStackProvider):
    assert stack.current == NamespaceTuple()


def test_pop_empty(stack: NamespaceStackProvider):
    with pytest.raises(AssertionError, match="Namespace stack must not be empty to pop"):
        stack.pop()
