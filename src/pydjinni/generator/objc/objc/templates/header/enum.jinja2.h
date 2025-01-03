/*#
Copyright 2023 - 2024 jothepro

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
typedef NS_ENUM(NSUInteger, {{ type_def.objc.name }}) {
//> for item in type_def.items:
    //? item.objc.comment : item.objc.comment | comment | indent
    {{ type_def.objc.name ~ item.objc.name ~  ("," if not loop.last) }}
//> endfor
}{{ type_def.objc.attributes | concat(prefix="\n") }};
//> endblock
