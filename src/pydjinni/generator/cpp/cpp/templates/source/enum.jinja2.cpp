/*> extends "base.jinja2" */

//> block content
//> if config.string_serialization:
//> call disable_deprecation_warnings(type_def.deprecated)
std::string to_string({{ type_def.cpp.typename }} value) noexcept {
    switch(value) {
        //> for item in type_def.items:
        //> call disable_deprecation_warnings(item.deprecated and not type_def.deprecated)
        case {{ type_def.cpp.typename }}::{{item.cpp.name}}: return "{{item.cpp.name}}";
        //> endcall
        //> endfor
    }
    return {};
}
//> endcall
//> endif
//> endblock
