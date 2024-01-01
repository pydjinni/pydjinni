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

import uuid
from pathlib import Path

import pytest

from pydjinni.parser.ast import Record
from pydjinni.parser.base_models import BaseExternalType
from pydjinni.parser.parser import Parser
from test_parser import given, when, given_mocks, assert_field


def test_parsing_record(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = record {
            bar: i8;
            baz: i8?;
        }
        """
    )

    record = when(parser, Record, "foo")

    fields = record.fields

    # THEN the record should have exactly 2 fields
    assert len(fields) == 2
    assert_field(fields[0], name="bar", typename="i8")
    assert_field(fields[1], name="baz", typename="i8", optional=True)
    assert not record.targets


@pytest.mark.parametrize("deriving,expected", [
    ('eq', {Record.Deriving.eq}),
    ('eq, ord', {Record.Deriving.eq, Record.Deriving.ord}),
    ('eq, ord, str', {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}),
    ('eq, eq', {Record.Deriving.eq})
])
def test_parsing_record_deriving(tmp_path: Path, deriving, expected: set[Record.Deriving]):
    # GIVEN an idl file that defines a record that derives some extensions
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
            foo = record {{
                baz: i8;
            }} deriving ({deriving})
            """
    )

    record = when(parser, Record, "foo")

    # THEN only the derived extensions should be enabled
    assert record.deriving == expected


def test_parsing_record_unknown_deriving(tmp_path: Path):
    # GIVEN an idl file that defines a record that derives an unknown extension
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl=f"""
                foo = record {{}} deriving (loremipsum)
                """
    )

    # WHEN parsing the input
    # THEN an error should be raised
    with pytest.raises(Parser.ParsingException, match="'loremipsum' is not a valid record extension"):
        parser.parse()


@pytest.mark.parametrize("deriving,expected", [
    ('', {Record.Deriving.eq, Record.Deriving.ord}),
    ('deriving()', {Record.Deriving.eq, Record.Deriving.ord}),
    ('deriving(ord)', {Record.Deriving.eq, Record.Deriving.ord}),
    ('deriving(eq, ord, str)', {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}),
])
def test_parsing_record_default_deriving(tmp_path: Path, deriving, expected: set[Record.Deriving]):
    reader, resolver_mock = given_mocks()

    # GIVEN an input file
    input_file = tmp_path / f"{uuid.uuid4()}.pydjinni"
    input_file.write_text(f"""
    foo = record {{}} {deriving}
    """)

    # AND GIVEN a Parser instance with a set of default deriving extensions
    parser = Parser(
        resolver=resolver_mock,
        file_reader=reader,
        targets=[],
        supported_target_keys=["cpp", "java"],
        include_dirs=[tmp_path],
        default_deriving={Record.Deriving.eq, Record.Deriving.ord},
        idl=input_file
    )

    # WHEN parsing the input
    # THEN the record should contain the defined default extensions
    record = when(parser, Record, "foo")
    assert record.deriving == expected

def test_parsing_record_ord_deriving_collection(tmp_path: Path):
    # GIVEN an idl file that defines a record with a collection that is deriving 'ord'
    parser, resolver_mock = given(
        tmp_path=tmp_path,
        input_idl="""
        foo = record {
            baz: list<i8>;
        } deriving(ord)
        """
    )
    resolver_mock.resolve.return_value = BaseExternalType(name='list', params=['T'], primitive=BaseExternalType.Primitive.collection)
    # WHEN parsing the input
    # THEN an exception should be thrown, because 'ord' is not allowed with collections
    with pytest.raises(Parser.ParsingException, match="Cannot compare collections in 'ord' deriving"):
        parser.parse()

def test_parsing_base_record(tmp_path: Path):
    # GIVEN an idl file that defines a record will be extended in C++
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
                foo = record +cpp {
                    baz: i8;
                }
                """
    )
    record = when(parser, Record, "foo")

    # THEN the target language C++ should be set
    assert len(record.targets) == 1
    assert 'cpp' in record.targets


def test_parsing_record_comment(tmp_path: Path):
    parser, _ = given(
        tmp_path=tmp_path,
        input_idl="""
            # This is a record
            # with a comment
            foo = record {
                # This is a record field
                baz: i8;
            }
            """
    )

    # WHEN parsing the input
    record = when(parser, Record, "foo")

    # THEN the record should contain the given comment
    assert record.comment == " This is a record\n with a comment"

    # THEN the field should contain the given comment
    assert record.fields[0].comment == " This is a record field"

