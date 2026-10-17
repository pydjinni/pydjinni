from more_itertools import one
from pytest_unordered import unordered

from pydjinni.parser.model.elements import (
    Enum,
    ErrorDomain,
    Flags,
    Function,
    Interface,
    Namespace,
    Parameter,
    Record,
    TypeReference,
)
from pydjinni.parser.model.identifier import Identifier

reference = TypeReference(
    name=Identifier("baz"),
    parameters=(),
)
second_reference = TypeReference(
    name=Identifier("foo"),
    parameters=(),
)
error_code = ErrorDomain.ErrorCode(
    name=Identifier("foo"),
    parameters=(),
)
error = ErrorDomain(
    name=Identifier("foo"),
    error_codes=(error_code,),
)
error_reference = TypeReference(
    name=Identifier("foo"),
    parameters=(),
)
parameter = Parameter(
    name=Identifier("foo"),
    reference=second_reference,
)


def test_record():
    field = Record.Field(
        name=Identifier("bar"),
        reference=reference,
    )
    record = Record(
        name=Identifier("foo"),
        fields=(field,),
    )

    assert one(record.children) == field
    assert one(field.children) == reference


def test_interface():
    method = Interface.Method(
        name=Identifier("method"),
        return_reference=reference,
        parameters=(parameter,),
        throwing=(error_reference,),
        static=False,
        const=False,
        asynchronous=False,
    )
    property = Interface.Property(
        name=Identifier("foo"),
        reference=reference,
        readonly=False,
    )
    interface = Interface(
        name=Identifier("bar"),
        params=(),
        methods=(method,),
        properties=(property,),
    )

    assert method.children == unordered(
        reference,
        parameter,
        error_reference,
    )
    assert one(property.children) == reference
    assert interface.children == unordered(
        method,
        property,
    )


def test_function():
    function = Function(
        name=Identifier("foo"),
        return_reference=reference,
        parameters=(parameter,),
        throwing=(error_reference,),
    )

    assert function.children == unordered(
        parameter,
        error_reference,
        reference,
    )


def test_namespace():
    namespace = Namespace(
        name=Identifier("foo"),
        types=(error,),
        namespaces=(),
    )

    assert one(namespace.children) == error


def test_enum():
    items = (
        Enum.Item(
            name=Identifier("foo"),
        ),
        Enum.Item(
            name=Identifier("bar"),
        ),
    )
    enum = Enum(
        name=Identifier("foobar"),
        items=items,
    )

    assert enum.children == unordered(items)


def test_flags():
    flag = Flags.Flag(
        name=Identifier("foo"),
        modifier=None,
    )

    flags = Flags(
        name=Identifier("bar"),
        flags=(flag,),
    )

    assert one(flags.children) == flag


def test_error_domain():
    error_code = ErrorDomain.ErrorCode(
        name=Identifier("some_error"),
        parameters=(parameter,),
    )

    error_domain = ErrorDomain(
        name=Identifier("error_domain"),
        error_codes=(error_code,),
    )

    assert one(error_domain.children) == error_code
    assert one(error_code.children) == parameter


def test_parameter():
    assert one(parameter.children) == second_reference
