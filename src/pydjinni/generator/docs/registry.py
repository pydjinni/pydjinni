

from attr import dataclass


class DocumentationTargetRegistry:
    @dataclass
    class DocumentationTarget:
        key: str
        display_key: str


    def __init__(self) -> None:
        self.documentation_targets: list[DocumentationTargetRegistry.DocumentationTarget] = []

    def register(self, documentation_target: DocumentationTarget):
        self.documentation_targets.append(documentation_target)
