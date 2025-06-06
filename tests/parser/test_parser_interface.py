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
import re
from pathlib import Path

import pytest

from pydjinni.parser.ast import Interface
from pydjinni.parser.base_models import BaseExternalType, TypeReference
from pydjinni.parser.parser import Parser
from test_parser import given, when, assert_exception


def assert_method(method: Interface.Method, name: str, params: list[tuple[str, str]] = None, return_type: str = None,
                  static: bool = False, const: bool = False, asynchronous: bool = False, throws: list[str] = None):
    assert method.name == name
    assert method.static == static
    assert method.const == const
    assert method.asynchronous == asynchronous
    if method.throwing is not None:
        assert [error.name for error in method.throwing ] == throws
    else:
        assert method.throwing == throws
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
    method_decls = [
        "method();",
        "static static_method();",
        "const const_method();",
        "async async_method();",
        "static async static_async_method();",
        "method_with_return() -> i8;",
        "method_with_parameter(param: i8);",
        "method_with_parameters_and_return(param: i8, param2: i8) -> i8;",
        "method_throwing() throws;",
        "method_throwing_and_return() throws -> i8;",
        "method_throwing_specific_error() throws application_error;",
        "method_throwing_specific_error_and_return() throws application_error -> i8;"
    ]
    property_decls = [
        "property a: i8;"
    ]
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = interface +cpp {{
                {" ".join(method_decls)}
                {" ".join(property_decls)}
            }}
            """
    )

    def mock_return_types(type_reference: TypeReference):
        if type_reference.name == "application_error":
            return BaseExternalType(name='application_error', primitive=BaseExternalType.Primitive.error)
        else:
            return BaseExternalType(name='<any>', primitive=BaseExternalType.Primitive.primitive)

    resolver_mock.resolve.side_effect = mock_return_types

    interface = when(parser, Interface, "foo")

    methods = interface.methods

    # THEN the interface should not be marked as 'main'
    assert not interface.main

    # THEN all the methods should have the expected names, parameters and attributes
    assert len(methods) == len(method_decls)
    assert_method(methods[0], "method")
    assert_method(methods[1], "static_method", static=True)
    assert_method(methods[2], "const_method", const=True)
    assert_method(methods[3], "async_method", asynchronous=True)
    assert_method(methods[4], "static_async_method", static=True, asynchronous=True)
    assert_method(methods[5], "method_with_return", return_type="i8")
    assert_method(methods[6], "method_with_parameter", params=[("param", "i8")])
    params = [("param", "i8"), ("param2", "i8")]
    assert_method(methods[7], "method_with_parameters_and_return", params=params, return_type="i8")
    assert_method(methods[8], "method_throwing", throws=[])
    assert_method(methods[9], "method_throwing_and_return", return_type="i8", throws=[])
    assert_method(methods[10], "method_throwing_specific_error", throws=["application_error"])
    assert_method(methods[11], "method_throwing_specific_error_and_return", return_type="i8", throws=["application_error"])

    # then the expected targets should be defined
    assert "cpp" in interface.targets
    assert len(interface.targets) == 1

    # then the defined properties should be present
    assert len(interface.properties) == len(property_decls)
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
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert exception.description == "Unknown interface target 'foo'"


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


@pytest.mark.parametrize("targets", ["-cpp", "+cpp +java"])
def test_parsing_interface_static_not_allowed(tmp_path, targets: str):
    # GIVEN an idl file that defines an interface with a static method
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = interface {targets} {{
                static foo();
            }}       
            """
    )

    # THEN a StaticNotAllowedException should be raised
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert exception.description == "methods are only allowed to be static on 'cpp' interfaces"


def test_parsing_interface_static_and_const_not_allowed(tmp_path: Path):
    # GIVEN an idl file that defines an interface with a static const method
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                static const foo();
            }       
            """
    )

    # THEN a ParsingException should be raised
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert exception.description == "method cannot be both static and const"

def test_parsing_interface_throwing_non_error_not_allowed(tmp_path: Path):
    # GIVEN an idl file that defines an interface with method that throws a non error type
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                foo() throws bar;
            }       
            """
    )

    resolver_mock.resolve.return_value = BaseExternalType(name="bar", primitive=BaseExternalType.Primitive.record)
    # THEN a ParsingException should be raised
    assert_exception(parser, "Only errors can be thrown")

def test_parsing_interface_returning_error_not_allowed(tmp_path: Path):
    # GIVEN an idl file that defines an interface with a method returning an error type
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = interface +cpp {
                foo() -> some_error;
            }
            """
    )
    resolver_mock.resolve.return_value = BaseExternalType(name="some_error", primitive=BaseExternalType.Primitive.error)

    # WHEN parsing the input
    # THEN an exception should be raised because returning an error type is not allowed
    assert_exception(parser, "Cannot return an error from a method")

def test_parsing_interface_error_parameter_not_allowed(tmp_path: Path):
    # GIVEN an idl file that defines an interface with a method that is passed an error type
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
                foo = interface +cpp {
                    foo(foo: some_error);
                }
                """
    )
    resolver_mock.resolve.return_value = BaseExternalType(name="some_error", primitive=BaseExternalType.Primitive.error)

    # WHEN parsing the input
    # THEN an exception should be raised because passing an error type as parameter is not allowed
    assert_exception(parser, "Cannot pass an error type to a method")

def test_parsing_main_interface(tmp_path: Path):
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
    assert_exception(parser, "a 'main' interface can only be implemented in C++")


def test_parsing_interface_comment(tmp_path: Path):
    # GIVEN an interface with comments
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
    assert interface.comment == "this interface is awesome\nit supports multiline comments"

    # THEN the method should contain the given comment
    assert interface.methods[0].comment == "this is the static initializer"

    # THEN the property should contain the given comment
    assert interface.properties[0].comment == "this is a property"


def test_parsing_comment_commands(tmp_path: Path):
    # GIVEN an interface with comments
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            # @deprecated but it should not be used
            foo = interface +cpp {
                # @param bar is a bar
                # @returns a foo instance
                # @deprecated
                static init_foo(bar: i8) -> foo;
            }
            """
    )

    # WHEN parsing the input
    interface = when(parser, Interface, "foo")

    # THEN the interface should be marked as deprecated
    assert interface.deprecated == "but it should not be used"

    # THEN the method should be marked as deprecated
    assert interface.methods[0].deprecated == True

    # THEN the method param should contain the @param docs
    assert interface.methods[0].parameters[0].comment == "is a bar"
