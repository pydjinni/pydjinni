from pathlib import Path

from pydjinni.parser.base_models import TypeReference


def quote(header: Path):
    return header if str(header).startswith("<") and str(header).endswith(">") else f'"{header}"'


def headers(dependencies: list[TypeReference], target: str) -> list[str]:
    header_paths: list[Path] = []
    for dependency_def in dependencies:
        header_path = getattr(dependency_def.type_def, target).header
        if header_path and (header_path not in header_paths):
            header_paths.append(header_path)
    return [quote(header) for header in header_paths]
