from pathlib import Path
from typing import Final

from dirty_equals import IsDict, IsPartialDict
from pydantic import TypeAdapter

from pydjinni.config.model.out_path import OutPaths, OutPathsLike, SingleOutPath


def test_single_out_path():
    path: Final = Path("foo.txt")

    out_path_like: Final = TypeAdapter(OutPathsLike).validate_python(path)

    assert isinstance(out_path_like, Path)
    assert isinstance(out_path_like, SingleOutPath)

    assert out_path_like == path
    assert out_path_like.header == path
    assert out_path_like.source == path


def test_out_paths():
    source_path: Final = Path("foo.txt")
    header_path: Final = Path("bar.txt")

    out_path_like: Final = TypeAdapter(OutPathsLike).validate_python({
        "source": source_path,
        "header": header_path,
    })

    assert isinstance(out_path_like, OutPaths)

    assert out_path_like.header == header_path
    assert out_path_like.source == source_path


def test_out_path_schema():
    schema: Final = TypeAdapter(OutPathsLike).json_schema()

    assert schema["$defs"]["OutPaths"] == IsPartialDict(
        properties=IsDict(
            source=IsPartialDict(format="path", type="string"),
            header=IsPartialDict(format="path", type="string"),
        ),
        required=["source", "header"],
    )
    assert schema["anyOf"] == [
        {"format": "path", "type": "string"},
        {"$ref": "#/$defs/OutPaths"},
    ]
