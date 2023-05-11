from pathlib import Path

from pydantic import BaseModel

from pydjinni.file.file_reader_writer import FileReaderWriter
from pydjinni.file.processed_files_model_builder import ProcessedFiles


def given() -> FileReaderWriter:
    # GIVEN a processed files model
    class ProcessedFilesModel(ProcessedFiles):
        class GeneratedFilesModel(BaseModel):
            class FooProcessedFilesList(BaseModel):
                source: list[Path] = []
                header: list[Path] = []
                include_dir: str = ""

            class BarProcessedFilesList(BaseModel):
                source: list[Path] = []

            foo: FooProcessedFilesList = FooProcessedFilesList()
            bar: BarProcessedFilesList = BarProcessedFilesList()

        generated: GeneratedFilesModel = GeneratedFilesModel()

    # GIVEN a FileReaderWriter
    reader_writer = FileReaderWriter()
    reader_writer.setup(ProcessedFilesModel)
    return reader_writer


def assert_generated_files(reader_writer: FileReaderWriter, foo_header: int = 0, foo_source: int = 0,
                           bar_source: int = 0):
    assert len(reader_writer.processed_files.generated.foo.header) == foo_header
    assert len(reader_writer.processed_files.generated.foo.source) == foo_source
    assert len(reader_writer.processed_files.generated.bar.source) == bar_source


def test_write_header_file(tmp_path: Path):
    writer = given()

    # WHEN writing a header file
    new_file_path = tmp_path / "foo.hpp"
    new_file_content = "header"
    writer.write_header(
        key="foo",
        filename=new_file_path,
        content=new_file_content)

    # THEN the file should exist
    assert new_file_path.exists()

    # THEN the file should have the expected content
    assert new_file_path.read_text() == new_file_content

    # THEN the file should have been recorded for the key 'foo'
    assert_generated_files(writer, foo_header=1)
    assert new_file_path in writer.processed_files.generated.foo.header


def test_write_source_file(tmp_path: Path):
    writer = given()

    # WHEN writing a source file
    new_file_path = tmp_path / "foo.cpp"
    new_file_content = "source"
    writer.write_source(
        key="foo",
        filename=new_file_path,
        content=new_file_content)

    # THEN the file should exist
    assert new_file_path.exists()

    # THEN the file should have the expected content
    assert new_file_path.read_text() == new_file_content

    # THEN the file should have been recorded for the key 'foo'
    assert_generated_files(writer, foo_source=1)
    assert new_file_path in writer.processed_files.generated.foo.source


def test_copy_header_directory(tmp_path: Path):
    writer = given()

    # AND GIVEN a header directory
    header_dir = tmp_path / "include"
    header_dir.mkdir()
    (header_dir / "header.hpp").touch()

    # WHEN copying the source directory
    target_dir = tmp_path / "target"
    writer.copy_header_directory(
        key="foo",
        header_dir=header_dir,
        target_dir=target_dir
    )

    # THEN the target dir should contain the file from the source dir
    target_file = target_dir / "header.hpp"
    assert target_file.exists()

    # THEN the file should be recorded in the list of output files
    assert_generated_files(writer, foo_header=1)
    assert target_file in writer.processed_files.generated.foo.header


def test_copy_source_directory(tmp_path: Path):
    writer = given()

    # AND GIVEN a header directory
    source_dir = tmp_path / "include"
    source_dir.mkdir()
    (source_dir / "source.cpp").touch()

    # WHEN copying the source directory
    target_dir = tmp_path / "target"
    writer.copy_source_directory(
        key="foo",
        source_dir=source_dir,
        target_dir=target_dir
    )

    # THEN the target dir should contain the file from the source dir
    target_file = target_dir / "source.cpp"
    assert target_file.exists()

    # THEN the file should be recorded in the list of output files
    assert_generated_files(writer, foo_source=1)
    assert target_file in writer.processed_files.generated.foo.source


def test_copy_missing_header_directory(tmp_path):
    writer = given()

    # WHEN copying a non-existent directory
    writer.copy_header_directory(key="foo", header_dir=tmp_path / "include", target_dir=tmp_path / "target")

    # THEN no copied files should be recorded
    assert_generated_files(writer)


def test_copy_missing_source_directory(tmp_path):
    writer = given()

    # WHEN copying a non-existent directory
    writer.copy_source_directory(key="foo", source_dir=tmp_path / "src", target_dir=tmp_path / "target")

    # THEN no copied files should be recorded
    assert_generated_files(writer)


def test_read_idl_file(tmp_path):
    reader = given()

    # AND GIVEN an idl file to read
    idl_file = tmp_path / "input.idl"
    content = "foo"
    idl_file.write_text(content)

    # WHEN reading the file
    read_content = reader.read_idl(idl_file)

    # THEN the correct file content sould be returned
    assert read_content == content

    # THEN the reading of the file should be recorded in the processed files model
    assert len(reader.processed_files.parsed.idl) == 1
    assert idl_file in reader.processed_files.parsed.idl


def test_read_external_type(tmp_path):
    reader = given()

    # AND given an external type definition
    external_type = tmp_path / "type.yaml"
    content = "foo"
    external_type.write_text(content)

    # WHEN reading the file
    read_content = reader.read_external_type(external_type)

    # THEN the correct file content sould be returned
    assert read_content == content

    # THEN the reading of the file should be recorded in the processed files model
    assert len(reader.processed_files.parsed.external_types) == 1
    assert external_type in reader.processed_files.parsed.external_types


def test_configure_include_dir():
    writer = given()

    include_dir = Path("foo_include_dir")

    # WHEN configuring the include_dir for an existing target
    writer.setup_include_dir("foo", include_dir)

    # THEN the processed files output should report the configured include directory
    assert writer.processed_files.generated.foo.include_dir == include_dir
