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


def test_parsing_inline_function(tmp_path):
    # GIVEN an interface with an inline function definition
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = interface {
            method(callback: function (var: i8));
        }
        """
    )
    # WHEN parsing the input
    ast = parser.parse()

    # THEN the anonymous type should be registered in the output AST
    assert len(ast) == 2
    assert isinstance(ast[0], Function)
    assert isinstance(ast[1], Interface)

    # THEN the method should reference an anonymous (nameless) function
    interface: Interface = ast[1]
    function = interface.methods[0].parameters[0].type_ref.type_def
    assert isinstance(function, Function)
    assert function.parameters[0].name == "var"
    assert function.return_type_ref is None


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
    with pytest.raises(Parser.ParsingException, match="functions are not allowed"):
        parser.parse()


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
