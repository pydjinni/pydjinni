from pathlib import Path

import pytest
from pydantic import BaseModel

from pydjinni.exceptions import InputParsingException
from pydjinni.file.file_handler import FileHandler


class SampleModel(BaseModel):
    name: str
    options: dict[str, int]


def test_read_resolves_relative_path_under_root(tmp_path: Path):
    handler = FileHandler(tmp_path)
    file = tmp_path / "input.txt"
    file.write_text("content")

    result = handler.read(Path("input.txt"))

    assert result == FileHandler.ReadResult(file, "content")


def test_read_keeps_absolute_path(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    file = tmp_path / "input.txt"
    file.write_text("content")
    handler = FileHandler(root)

    result = handler.read(file)

    assert result == FileHandler.ReadResult(file, "content")


def test_init_rejects_file_as_root(tmp_path: Path):
    root = tmp_path / "file"
    root.touch()

    with pytest.raises(ValueError, match="root path must be a directory"):
        FileHandler(root)


def test_write_creates_parent_directories(tmp_path: Path):
    handler = FileHandler(tmp_path)

    written_file = handler.write(
        Path("nested/output.txt"),
        "content",
    )

    assert written_file == tmp_path / "nested/output.txt"
    assert written_file.read_text() == "content"


@pytest.mark.parametrize(
    "suffix",
    [
        ".yaml",
        ".yml",
        ".json",
        ".json5",
        ".toml",
    ],
)
def test_write_and_read_model_round_trip(tmp_path: Path, suffix: str):
    handler = FileHandler(tmp_path)
    model = SampleModel(
        name="example",
        options={
            "timeout": 30,
            "retries": 2,
        },
    )
    file = Path(f"nested/config{suffix}")

    written_file = handler.write_model(file, model)
    result = handler.read_model(file, SampleModel)

    assert written_file == tmp_path / file
    assert written_file.is_file()
    assert result == FileHandler.ReadResult(written_file, model)


def test_read_model_merges_additional_nested_options(tmp_path: Path):
    handler = FileHandler(tmp_path)
    file = tmp_path / "config.json"
    file.write_text('{"name": "example", "options": {"timeout": 30, "retries": 2}}')

    result = handler.read_model(
        Path("config.json"),
        SampleModel,
        frozendict({
            "options": {
                "retries": 5,
                "workers": 4,
            }
        }),
    )

    assert result.content == SampleModel(
        name="example",
        options={
            "timeout": 30,
            "retries": 5,
            "workers": 4,
        },
    )


def test_read_model_reports_json5_parse_error(tmp_path: Path):
    handler = FileHandler(tmp_path)
    file = tmp_path / "invalid.json5"
    file.write_text("{name: }")

    with pytest.raises(InputParsingException) as error:
        handler.read_model(Path("invalid.json5"), SampleModel)

    assert error.value.position is not None
    assert error.value.position.file == file


def test_write_model_rejects_unknown_extension(tmp_path: Path):
    handler = FileHandler(tmp_path)
    model = SampleModel(name="example", options={})

    with pytest.raises(ValueError, match="Unknown model dump file extension"):
        handler.write_model(Path("config.ini"), model)


def test_copy_file_to_destination_directory(tmp_path: Path):
    handler = FileHandler(tmp_path)
    source = tmp_path / "source.txt"
    source.write_text("content")
    destination = tmp_path / "output" / "source.txt"

    copied_file = handler.copy(source, destination)

    assert copied_file == destination
    assert copied_file.read_text() == "content"


def test_copy_directory_preserves_nested_paths_and_filenames(tmp_path: Path):
    handler = FileHandler(tmp_path)
    source = tmp_path / "source"
    (source / "nested").mkdir(parents=True)
    (source / "top.txt").write_text("top")
    (source / "nested" / "inner.txt").write_text("inner")

    copied_files = set(handler.copy_directory(Path("source"), Path("destination")))

    assert copied_files == {
        tmp_path / "destination" / "top.txt",
        tmp_path / "destination" / "nested" / "inner.txt",
    }
    assert (tmp_path / "destination" / "top.txt").read_text() == "top"
    assert (tmp_path / "destination" / "nested" / "inner.txt").read_text() == "inner"
