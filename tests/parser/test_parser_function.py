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

from pydjinni.parser.ast import Function, Interface
from pydjinni.parser.base_models import BaseExternalType
from test_parser import given, when, assert_exception


def test_parsing_function(tmp_path):
    # GIVEN a named function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="foo = function +cpp (param: i8) -> bool;"
    )

    function = when(parser, Function, "foo")

    # THEN the function should have the expected parameters and return type
    assert len(function.parameters) == 1
    assert function.parameters[0].name == "param"
    assert function.parameters[0].type_ref.name == "i8"
    assert function.return_type_ref.name == "bool"
    assert function.throwing is None
    # THEN all the specified language target should be set
    assert "cpp" in function.targets
    assert len(function.targets) == 1


def test_parsing_function_no_target(tmp_path: Path):
    # GIVEN a named function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="foo = function (param: i8) -> bool;"
    )

    function = when(parser, Function, "foo")

    # THEN all known language targets should be set for the defined interface
    assert "cpp" in function.targets
    assert "java" in function.targets
    assert len(function.targets) == 2


def test_parsing_function_minus_target(tmp_path: Path):
    # GIVEN a named function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="foo = function -cpp (param: i8) -> bool;"
    )

    function = when(parser, Function, "foo")

    # THEN all known language targets minus the one specified in the interface should be set for the defined interface
    assert "java" in function.targets
    assert len(function.targets) == 1


def test_parsing_inline_function(tmp_path: Path):
    # GIVEN an interface with an inline function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = interface {
            method0(callback: function (var: i8));
        }
        """
    )
    # WHEN parsing the input
    defs, _, _ = parser.parse()

    # THEN the anonymous type should be registered in the output type_defs
    assert len(defs) == 2
    assert isinstance(defs[0], Function)
    assert isinstance(defs[1], Interface)

    interface: Interface = defs[1]

    def assert_function(index: int):
        # THEN the method should reference an anonymous (nameless) function
        function = interface.methods[index].parameters[0].type_ref.type_def
        assert isinstance(function, Function)
        assert function.parameters[0].name == "var"
        assert function.return_type_ref is None

    assert_function(0)


def test_parsing_anonymous_function_not_allowed(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = record {
                field: ();
            }
            """
    )

    # WHEN parsing the input
    # THEN a ParsingException should be raised because functions are not allowed in records
    assert_exception(parser, "functions are not allowed as record field type")

def test_parsing_function_throwing(tmp_path: Path):
    # GIVEN a function that throws
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = function () throws;
            """
    )

    # WHEN parsing the input
    ast, _, _ = parser.parse()

    # THEN the parsed function should be marked as throwing
    assert len(ast) == 1
    function = ast[0]
    assert isinstance(function, Function)
    assert function.throwing is not None

def test_parsing_function_throwing_specific_error(tmp_path: Path):
    # GIVEN a function that throws the error `bar`
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = function () throws bar;
            """
    )
    resolver_mock.resolve.return_value = BaseExternalType(name="bar", primitive=BaseExternalType.Primitive.error)

    # WHEN parsing the input
    ast, _, _ = parser.parse()

    # THEN the parsed function should be marked as throwing `bar`
    assert len(ast) == 1
    function = ast[0]
    assert isinstance(function, Function)
    assert function.throwing is not None
    assert function.throwing[0].name == "bar"

def test_parsing_function_throwing_non_error_not_allowed(tmp_path: Path):
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = function () throws bar;
            """
    )

    resolver_mock.resolve.return_value = BaseExternalType(name="bar", primitive=BaseExternalType.Primitive.record)

    # THEN a ParsingException should be raised
    assert_exception(parser, "Only errors can be thrown")

def test_parsing_function_returning_error_not_allowed(tmp_path: Path):
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = function () -> some_error;
            """
    )
    resolver_mock.resolve.return_value = BaseExternalType(name="some_error", primitive=BaseExternalType.Primitive.error)

    # WHEN parsing the input
    # THEN an exception should be raised, because returning an error from a function is not allowed
    assert_exception(parser, "Cannot return an error type from a function")

def test_parsing_function_error_parameter_not_allowed(tmp_path: Path):
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
            foo = function (param: some_error);
            """
    )
    resolver_mock.resolve.return_value = BaseExternalType(name="some_error", primitive=BaseExternalType.Primitive.error)
    # WHEN parsing the input
    # THEN an exception should be raised, because passing an error to a function is not allowed
    assert_exception(parser, "Cannot pass an error type to a function")

def test_parsing_function_comment(tmp_path: Path):
    # GIVEN a named function with comment
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
                # this function does nothing
                foo = function ();
                """
    )

    # WHEN parsing the input
    function = when(parser, Function, "foo")

    # THEN the function should contain the given comment
    assert function.comment == " this function does nothing"
