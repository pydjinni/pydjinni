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

//> set counter = namespace(value=0)

//> block content
//? type_def.cppcli.comment : type_def.cppcli.comment | comment
[System::Flags]
//? type_def.deprecated : type_def.cppcli.deprecated
public enum class {{ type_def.cppcli.name }} {
    //> for flag in type_def.flags:
    //? flag.cppcli.comment : flag.cppcli.comment | comment | indent
    //? flag.deprecated : flag.cppcli.deprecated | indent
    {{ flag.cppcli.name ~ " = "-}}
    /*> if flag.none */
        {{- "0" -}}
    /*> elif flag.all */
        {{- "0 | " -}}
        /*> for flag in type_def.flags if not flag.none and not flag.all */
            {{- flag.cppcli.name ~ (" | " if not loop.last) -}}
        /*> endfor */
    /*> else */
        {{- "1u << " ~ counter.value -}}
        /*> set counter.value = counter.value + 1 */
    //> endif
    {{- ("," if not loop.last) }}
    //> endfor
};
//> endblock
