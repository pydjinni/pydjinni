from pathlib import Path

from pydjinni.generator.file_writer import FileWriter


def test_write_file(tmp_path: Path):
    # GIVEN a file writer
    writer = FileWriter()

    # WHEN writing a file
    new_file_path = tmp_path / "foo.txt"
    new_file_content = "foo"
    writer.write(new_file_path, new_file_content)

    # THEN the file should exist
    assert new_file_path.exists()

    # THEN the file should have the expected content
    assert new_file_path.read_text() == new_file_content

    # THEN the file writing should have been recorded
    assert len(writer.generated_files) == 1
    assert new_file_path in writer.generated_files


def test_copy_file(tmp_path: Path):
    # GIVEN a file writer
    writer = FileWriter()

    # AND GIVEN a source file
    source_file = tmp_path / "source.txt"
    source_file.write_text("source")

    # WHEN copying the source file
    target_file = tmp_path / "target.txt"
    writer.copy(source_file, target_file)

    # THEN the file should be copied
    assert target_file.exists()
    assert target_file.read_text() == "source"

    # THEN the file should be recorded in the list of output files
    assert len(writer.generated_files) == 1
    assert target_file in writer.generated_files


def test_copy_directory(tmp_path: Path):
    # GIVEN a file writer
    writer = FileWriter()

    # AND GIVEN a source directory
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "file.txt").touch()

    # WHEN copying the source directory
    target_dir = tmp_path / "target"
    writer.copy_directory(source_dir, target_dir)

    # THEN the target dir should contain the file from the source dir
    target_file = target_dir / "file.txt"
    assert target_file.exists()

    # THEN the copied file should be recorded in the list of output files
    assert len(writer.generated_files) == 1
    assert target_file in writer.generated_files


def test_copy_missing_directory(tmp_path):
    # GIVEN a file writer
    writer = FileWriter()

    # WHEN copying a non-existent directory
    writer.copy_directory(tmp_path / "source", tmp_path / "target")

    # THEN no copied files should be recorded
    assert len(writer.generated_files) == 0
