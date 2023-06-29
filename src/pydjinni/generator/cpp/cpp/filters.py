from pydjinni.parser.base_models import TypeReference


def needs_optional(dependencies: list[TypeReference]):
    for dependency_def in dependencies:
        if dependency_def.optional:
            return True
        needs_optional(dependency_def.parameters)
    return False
