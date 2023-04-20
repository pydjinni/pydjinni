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

    def write_generated_files(self, filename: Path):
        self.write(filename, '\n'.join([str(file) for file in self.generated_files]))
