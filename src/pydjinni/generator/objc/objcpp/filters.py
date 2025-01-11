from pydjinni.parser.base_models import TypeReference

def translator(type_ref: TypeReference) -> str:
    output = type_ref.type_def.objcpp.translator
    if type_ref.parameters:
        output = f"{output}<{','.join([translator(parameter_ref) for parameter_ref in type_ref.parameters])}>"
    if type_ref.optional:
        output = f"::pydjinni::translators::objc::Optional<std::optional,{output}>"
    return output
