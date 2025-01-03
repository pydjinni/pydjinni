/*#
Copyright 2023 jothepro

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
FOUNDATION_EXPORT NSErrorDomain const {{ type_def.objc.domain_name }};
//? type_def.objc.comment : type_def.objc.comment | comment
typedef NS_ERROR_ENUM({{ type_def.objc.domain_name }}, {{ type_def.objc.name }}) {
    /*> for error_code in type_def.error_codes */
    //? error_code.objc.comment : error_code.objc.comment | comment | indent
    {{ type_def.objc.name ~ error_code.objc.name ~ (error_code.objc.attributes | concat(prefix="\n") | indent )  ~ ("," if not loop.last) }}
    /*> endfor */
}{{ type_def.objc.attributes | concat(prefix='\n') }};

//> for user_info_key in type_def.objc.user_info_keys:
FOUNDATION_EXPORT NSErrorUserInfoKey const {{ user_info_key.objc }}
/*>- if config.swift.rename_interfaces */
 NS_SWIFT_NAME({{ user_info_key.swift }})
/*>- endif -*/;
//> endfor
//> endblock
