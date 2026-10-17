from more_itertools import one

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import Interface
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.processing.processors.method_checks import MethodChecks


def test_method_static_and_const():
    # GIVEN an Interface Method that is both 'const' and 'static'
    method = Interface.Method(
        name=Identifier("foo"),
        static=True,
        const=True,
        return_reference=None,
        asynchronous=False,
        parameters=(),
        throwing=(),
    )

    # AND GIVEN a MethodChecks instance
    checks = MethodChecks()

    # WHEN executing the checks against the method
    parse_result = checks.process(method)

    # THEN a ParseIssue should be raised because a method cannot be both static and const
    assert one(parse_result.diagnostics) == Diagnostic(
        position=method.position,
        description="method cannot be both static and const",
        severity=Diagnostic.Severity.error,
    )
