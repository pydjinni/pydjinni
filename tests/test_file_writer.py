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
    assert writer.generated_files[0] == new_file_path

