import shutil
from pathlib import Path


class FileWriter:
    """
    use this class to write a generated file. This way the writing will be recorded and the generated file will be
    added to the list of generated files.
    """
    def __init__(self):
        self._generated_files: list[Path] = []
        self._list_out_files_path: Path | None = None

    @property
    def generated_files(self) -> list[Path]:
        return self._generated_files

    def write(self, filename: Path, content: str, append: bool = True):
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(content)
        if append:
            self._generated_files.append(filename)

    def copy(self, source_file: Path, target_file: Path, append: bool = True):
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source_file, target_file)
        if append:
            self._generated_files.append(target_file)

    def copy_directory(self, source_dir: Path, target_dir: Path, append: bool = True):
        if source_dir.exists():
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    target_file_path = target_dir / file_path.relative_to(source_dir)
                    self.copy(file_path, target_file_path, append=append)

    def write_generated_files(self, filename: Path):
        self.write(filename, '\n'.join([str(file) for file in self.generated_files]))
