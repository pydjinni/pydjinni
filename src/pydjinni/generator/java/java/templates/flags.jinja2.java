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
//? type_def.comment : type_def.java.comment | comment
//? type_def.deprecated : "@Deprecated"
public enum {{ type_def.java.name }} {
//> for flag in type_def.flags if not flag.none and not flag.all:
    //? flag.comment : flag.java.comment | comment | indent
    //? flag.deprecated : "@Deprecated"
    {{ flag.java.name ~ (";" if loop.last else ",") }}
//> endfor
}
//> endblock
