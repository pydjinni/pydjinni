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
//? type_def.objc.comment : type_def.objc.comment | comment
//? type_def.objc.attributes : type_def.objc.attributes | join('\n')
//> if "objc" in type_def.targets:
@protocol {{ type_def.objc.name }} {{ "<NSObject>" if config.strict_protocols }}
//> else:
@interface {{ type_def.objc.name }} : NSObject
//> endif
//> for method in type_def.methods
//? method.objc.comment : method.objc.comment | comment
{{ method.objc.specifier }} ({{ (((method.objc.annotation ~ " ") if method.objc.annotation) ~ method.objc.type_decl) if not method.asynchronous else "void" }}){{ method.objc.name }}
//>- for parameter in method.objc.parameters:
{{ ":" if loop.first else ( " " ~ parameter.name ~ ":") }}({{ ((parameter.annotation ~ " ") if parameter.annotation) ~ parameter.type_decl }}){{ parameter.name }}
//>- endfor
{{ method.objc.attributes | concat(prefix='\n') | indent(2) }};
//> endfor
@end
//> endblock
