/*#
Copyright 2024 jothepro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#*/
//> extends "base.jinja2"

//> block content
auto {{ type_def.objcpp.name }}::toCpp(::NSError* obj) -> std::exception_ptr {
    assert(obj);
    switch(obj.code) {
        /*> for error_code in type_def.error_codes */
        case {{ type_def.objc.name ~ error_code.objc.name }}:
            return std::make_exception_ptr({{ type_def.cpp.typename }}::{{ error_code.cpp.name }}(
                /*> for parameter in error_code.parameters */
                {{ parameter.objcpp.translator }}::Boxed::toCpp([obj.userInfo valueForKey:{{ type_def.objc.user_info_keys[loop.index - 1].objc }}]),
                /*> endfor */
                ::pydjinni::translators::objc::String::toCpp(obj.localizedDescription)
            ));
        /*> endfor */
    }
    return {};
}

/*> for error_code in type_def.error_codes */
auto {{ type_def.objcpp.name }}::fromCpp(const {{ type_def.cpp.typename }}::{{ error_code.cpp.name }}& cpp) -> ::NSError* {
    NSString *desc = NSLocalizedString(::pydjinni::translators::objc::String::fromCpp(cpp.what()), @"");
    NSDictionary *userInfo = @{ NSLocalizedDescriptionKey : desc
    /*>- for parameter in error_code.parameters -*/
        , {{ type_def.objc.user_info_keys[loop.index - 1].objc }}: {{ parameter.objcpp.translator }}::Boxed::fromCpp(cpp.{{ parameter.cpp.name }})
    /*>- endfor -*/
    };
    return [NSError errorWithDomain:{{ type_def.objc.domain_name }}
                               code:{{ type_def.objc.name ~ error_code.objc.name }}
                           userInfo:userInfo];
}
/*> endfor */
//> endblock
