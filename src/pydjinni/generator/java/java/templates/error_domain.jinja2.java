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
//? type_def.comment : type_def.java.comment | comment
//? type_def.deprecated : "@Deprecated"
public abstract class {{ type_def.java.name }} extends Exception {
    public {{ type_def.java.name }}(String message) {
        super(message);
    }
//> for error_code in type_def.error_codes:
    //? error_code.comment : error_code.java.comment | comment | indent
    //? error_code.deprecated : "@Deprecated"
    public final static class {{ error_code.java.name }} extends {{ type_def.java.name }} {
    //> for parameter in error_code.parameters:
        //? parameter.comment : parameter.java.comment | comment | indent(8)
        //? parameter.deprecated : "@Deprecated"
        {{ parameter.java.field_modifier ~ parameter.java.data_type }} {{ parameter.java.name }};
    //> endfor

        public {{ error_code.java.name }}(
        //> for parameter in error_code.parameters:
            {{ parameter.java.data_type }} {{ parameter.java.name ~ ("," if not loop.last) }}
        //> endfor
        ) {
            this(
            /*>- for parameter in error_code.parameters -*/
                {{ parameter.java.name ~ ", " }}
            /*>- endfor -*/
            null);
        }

        public {{ error_code.java.name }}(
            //> for parameter in error_code.parameters:
            {{ parameter.java.data_type }} {{ parameter.java.name }},
            //> endfor
            String message
        ) {
            super(message);
            //> for parameter in error_code.parameters:
            this.{{ parameter.java.name }} = {{ parameter.java.name }};
            //> endfor
        }

    //> for parameter in error_code.parameters:
        //? parameter.comment : parameter.java.comment | comment | indent(8)
        //? parameter.deprecated : "@Deprecated"
        public {{ parameter.java.data_type }} {{ parameter.java.getter }}() { return {{ parameter.java.name }}; }
    //> endfor
    }
//> endfor
}
//> endblock
