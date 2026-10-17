from pydjinni.parser.model.namespace_tuple import NamespaceTuple
lazy from pydjinni.parser.model.identifier import Identifier


class NamespaceStackProvider:
    def __init__(self) -> None:
        self._stack: list[Identifier] = []
        self._current_context_size: list[int] = []

    @property
    def current(self) -> NamespaceTuple:
        return NamespaceTuple(values=tuple(self._stack))

    def push(self, namespace_tuple: NamespaceTuple):
        self._stack += namespace_tuple.values
        self._current_context_size.append(len(namespace_tuple.values))

    def pop(self):
        assert len(self._stack) > 0, "Namespace stack must not be empty to pop"
        del self._stack[-self._current_context_size.pop() :]
