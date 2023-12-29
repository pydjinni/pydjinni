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

from pathlib import Path

import pytest

from pydjinni.parser.ast import Interface
from pydjinni.parser.parser import Parser
from test_parser import given, when


def assert_method(method: Interface.Method, name: str, params: list[tuple[str, str]] = None, return_type: str = None,
                  static: bool = False, const: bool = False):
    assert method.name == name
    assert method.static == static
    assert method.const == const
    if return_type:
        assert method.return_type_ref.name == return_type
    else:
        assert method.return_type_ref is None
    if params:
        assert len(method.parameters) == len(params)
        for param in method.parameters:
            assert (param.name, param.type_ref.name) in params
    else:
        assert len(method.parameters) == 0


def test_parsing_interface(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                method();
                static static_method();
                const const_method();
                method_with_return() -> i8;
                method_with_parameter(param: i8);
                method_with_parameters_and_return(param: i8, param2: i8) -> i8;
                property a: i8;
            }
            """
    )

    interface = when(parser, Interface, "foo")

    methods = interface.methods

    # THEN the interface should not be marked as 'main'
    assert not interface.main

    # THEN the interface should have exactly 5 methods
    assert len(methods) == 6

    # THEN the methods should have the expected names, parameters and attributes
    assert_method(methods[0], "method")
    assert_method(methods[1], "static_method", static=True)
    assert_method(methods[2], "const_method", const=True)
    assert_method(methods[3], "method_with_return", return_type="i8")
    assert_method(methods[4], "method_with_parameter", params=[("param", "i8")])
    params = [("param", "i8"), ("param2", "i8")]
    assert_method(methods[5], "method_with_parameters_and_return", params=params, return_type="i8")

    # then the expected targets should be defined
    assert "cpp" in interface.targets
    assert len(interface.targets) == 1

    # then the defined properties should be present
    assert len(interface.properties) == 1
    property_def = interface.properties[0]
    assert property_def.name == "a"
    assert property_def.type_ref.name == "i8"


def test_parsing_interface_unknown_target(tmp_path: Path):
    # GIVEN an idl file that references an unknown target language for the defined interface
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +foo {
                method();
            }
            """
    )
    # WHEN parsing the input
    # THEN a IdlParser.UnknownInterfaceTargetException should be raised
    with pytest.raises(Parser.ParsingException, match="Unknown interface target 'foo'"):
        parser.parse()


def test_parsing_interface_no_target(tmp_path: Path):
    # GIVEN an idl file that references no target language for the defined interface
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface {
                method();
            }
            """
    )
    # WHEN parsing the input
    interface = when(parser, Interface, "foo")
    # THEN all known interface targets should be set for the defined interface
    assert "cpp" in interface.targets
    assert "java" in interface.targets
    assert len(interface.targets) == 2


def test_parsing_interface_minus_target(tmp_path: Path):
    # GIVEN an idl file that only references the exclusion of a target from the defined interface
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface -cpp {
                method();
            }
            """
    )
    # WHEN parsing the input
    interface = when(parser, Interface, "foo")
    # THEN all known interface targets except the one excluded should be present in the interface
    assert "java" in interface.targets
    assert len(interface.targets) == 1


def test_parsing_interface_static_not_allowed(tmp_path):
    # GIVEN an idl file that defines an interface with a static method that is not targeting `cpp`
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface -cpp {
                static foo();
            }       
            """
    )

    # THEN a StaticNotAllowedException should be raised
    with pytest.raises(Parser.ParsingException, match="methods are only allowed to be static on 'cpp' interfaces"):
        parser.parse()


def test_parsing_interface_static_and_const_not_allowed(tmp_path):
    # GIVEN an idl file that defines an interface with a static const method
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                static const foo();
            }       
            """
    )

    # THEN a StaticAndConstException should be raised
    with pytest.raises(Parser.ParsingException, match="method cannot be both static and const"):
        parser.parse()


def test_parsing_main_interface(tmp_path):
    # GIVEN an idl file that defines a main interface (code entrypoint)
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = main interface +cpp {}       
            """
    )
    # WHEN parsing the input
    interface = when(parser, Interface, "foo")

    # THEN the interface should be marked as 'main'
    assert interface.main


@pytest.mark.parametrize("targets", ["-cpp", "+cpp +java"])
def test_parsing_main_interface_not_cpp(tmp_path, targets):
    # GIVEN an idl file that defines a main interface (code entrypoint)
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = main interface {targets} {{}}       
            """
    )
    # WHEN parsing the input
    # THEN a ParsingException should be thrown because the 'main' interface is not implemented in C++
    with pytest.raises(Parser.ParsingException, match=r"a 'main' interface can only be implemented in C++"):
        parser.parse()


def test_parsing_interface_comment(tmp_path: Path):
    # GIVEN an interface with a comments
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            # this interface is awesome
            # it supports multiline comments
            foo = interface +cpp {
                # this is the static initializer
                static init_foo() -> foo;
                
                # this is a property
                property foo: i8;
            }
            """
    )

    # WHEN parsing the input
    interface = when(parser, Interface, "foo")

    # THEN the interface should contain the given comment
    assert interface.comment == " this interface is awesome\n it supports multiline comments"

    # THEN the method should contain the given comment
    assert interface.methods[0].comment == " this is the static initializer"

    # THEN the property should contain the given comment
    assert interface.properties[0].comment == " this is a property"
