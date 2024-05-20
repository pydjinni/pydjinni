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
from pydjinni.parser.parser import Parser
from test_parser import given, when


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
    # THEN all the specified language target should be set
    assert "cpp" in function.targets
    assert len(function.targets) == 1
    assert not function.asynchronous
    assert not function.throws


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


@pytest.mark.parametrize("input_idl", [
    "foo = async function () -> bool;",
    "foo = async (param: i8);"
])
def test_parsing_async_function(tmp_path: Path, input_idl: str):
    # GIVEN a named async function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=input_idl
    )

    function = when(parser, Function, "foo")
    assert function.asynchronous


@pytest.mark.parametrize("input_idl", [
    "foo = function () throws -> bool;",
    "foo = (param: i8) throws;",
    "foo = async function () throws -> bool;",
    "foo = async (param: i8) throws;"
])
def test_parsing_throwing_function(tmp_path: Path, input_idl: str):
    # GIVEN a named function definition that throws
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=input_idl
    )

    function = when(parser, Function, "foo")
    assert function.throws


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
            method1(callback: async function (var: i8));
            method2(callback: async (var: i8));
        }
        """
    )
    # WHEN parsing the input
    ast, _ = parser.parse()

    # THEN the anonymous type should be registered in the output AST
    assert len(ast) == 4
    assert isinstance(ast[0], Function)
    assert isinstance(ast[1], Function)
    assert isinstance(ast[2], Function)
    assert isinstance(ast[3], Interface)

    interface: Interface = ast[3]

    def assert_function(index: int, asynchronous: bool = False):
        # THEN the method should reference an anonymous (nameless) function
        function = interface.methods[index].parameters[0].type_ref.type_def
        assert isinstance(function, Function)
        assert function.parameters[0].name == "var"
        assert function.return_type_ref is None
        assert function.asynchronous == asynchronous

    assert_function(0)
    assert_function(1, asynchronous=True)
    assert_function(2, asynchronous=True)


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
    with pytest.raises(Parser.ParsingExceptionList) as excinfo:
        parser.parse()
    assert len(excinfo.value.items) == 1
    exception = excinfo.value.items[0]
    assert isinstance(exception, Parser.ParsingException)
    assert exception.description == "functions are not allowed as record field type"


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
