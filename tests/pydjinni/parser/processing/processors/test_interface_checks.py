from unittest.mock import Mock

import pytest
from more_itertools import one

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.parser.model.elements import ClassType, Interface
from pydjinni.parser.model.identifier import Identifier
from pydjinni.parser.processing.processors.interface_checks import InterfaceChecks
from pydjinni.position import Position


@pytest.fixture
def interface_checks() -> InterfaceChecks:
    # GIVEN a InterfaceChecks instance
    return InterfaceChecks()


def test_valid_interface(interface_checks: InterfaceChecks):
    # GIVEN a valid interface
    interface = Interface(
        name=Identifier("foo"),
        methods=(
            Interface.Method(
                name=Identifier("foo"),
                static=False,
                const=False,
                return_reference=None,
                asynchronous=False,
                parameters=(),
                throwing=(),
            ),
        ),
    )

    # WHEN executing the checks against the interface
    parse_result = interface_checks.process(interface)

    # THEN no parse issues should be reported
    assert len(parse_result.diagnostics) == 0


def test_valid_static_method(interface_checks: InterfaceChecks):
    # GIVEN a valid static method on a native interface
    interface = Interface(
        name=Identifier("foo"),
        target=ClassType.Target.native,
        methods=(
            Interface.Method(
                name=Identifier("foo"),
                static=True,
                const=False,
                return_reference=None,
                asynchronous=False,
                parameters=(),
                throwing=(),
            ),
        ),
    )

    # WHEN executing the checks against the interface
    parse_result = interface_checks.process(interface)

    # THEN no parse issues should be reported
    assert len(parse_result.diagnostics) == 0


@pytest.mark.parametrize(
    "target",
    (ClassType.Target.shared, ClassType.Target.host),
)
def test_static_method_for_host_target(interface_checks: InterfaceChecks, target: ClassType.Target):
    method_position = Mock(Position)
    # GIVEN a static method on an host interface
    interface = Interface(
        name=Identifier("foo"),
        target=target,
        methods=(
            Interface.Method(
                position=method_position,
                name=Identifier("foo"),
                static=True,
                const=False,
                return_reference=None,
                asynchronous=False,
                parameters=(),
                throwing=(),
            ),
        ),
    )

    # WHEN executing the checks against the interface
    parse_result = interface_checks.process(interface)

    # THEN a static method target parse issue should be reported
    assert one(parse_result.diagnostics) == Diagnostic(
        position=method_position,
        description="static methods are only allowed on native or main interfaces",
        severity=Diagnostic.Severity.error,
    )
