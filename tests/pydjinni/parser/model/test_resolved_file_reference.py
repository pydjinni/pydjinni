from pathlib import Path

from pydjinni.parser.model.elements import ResolvedFileReference
from pydjinni.position import Position


def test_no_circular_import(tmp_path: Path):
    # GIVEN a chain of FileReferences
    first_path = Path("a.pydjinni")
    first_absolute_path = tmp_path / first_path
    first_file_reference = ResolvedFileReference(
        path=first_path,
        resolved_path=first_absolute_path,
    )

    second_path = Path("b.pydjinni")
    second_absolute_path = tmp_path / second_path
    second_file_reference = ResolvedFileReference(
        position=Position.from_file(first_absolute_path),
        path=second_path,
        resolved_path=second_absolute_path,
        parent=first_file_reference,
    )

    third_path = Path("c.pydjinni")
    third_absolute_path = tmp_path / third_path
    third_file_reference = ResolvedFileReference(
        position=Position.from_file(second_absolute_path),
        path=third_path,
        resolved_path=third_absolute_path,
        parent=second_file_reference,
    )

    # WHEN checking for circular imports
    import_chain = third_file_reference.circular_import_chain

    # THEN no circular import should be reported
    assert not import_chain


def test_circular_import(tmp_path: Path):
    # GIVEN a chain of FileReferences with a circular dependency
    first_path = Path("a.pydjinni")
    first_absolute_path = tmp_path / first_path
    first_file_reference = ResolvedFileReference(
        path=first_path,
        resolved_path=first_absolute_path,
    )

    second_path = Path("b.pydjinni")
    second_absolute_path = tmp_path / second_path
    second_file_reference = ResolvedFileReference(
        position=Position.from_file(first_absolute_path),
        path=second_path,
        resolved_path=second_absolute_path,
        parent=first_file_reference,
    )

    third_file_reference = ResolvedFileReference(
        position=Position.from_file(second_absolute_path),
        path=first_path,
        resolved_path=first_absolute_path,
        parent=second_file_reference,
    )

    # WHEN checking for circular imports
    import_chain = third_file_reference.circular_import_chain

    # THEN the circular import should be reported
    assert import_chain == (second_file_reference, third_file_reference)
