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
struct {{ type_def.cpp.deprecated ~ type_def.objcpp.name }} {
    static std::exception_ptr toCpp(::NSError* objc);
    /*> for error_code in type_def.error_codes */
    static ::NSError* fromCpp(const {{ type_def.cpp.typename }}::{{ error_code.cpp.name }}& cpp);
    /*> endfor */
};
//> endblock
