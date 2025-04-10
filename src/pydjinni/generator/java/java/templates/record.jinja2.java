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
{{ type_def.java.class_modifier }}class {{ type_def.java.name }} {
//> for field in type_def.fields
    {{ field.java.field_modifier ~ field.java.data_type }} {{ field.java.name }};
//> endfor
    public {{ type_def.java.name }}(
    //> for field in type_def.fields:
        {{ field.java.data_type }} {{ field.java.name ~ ("," if not loop.last) }}
    //> endfor
    ) {
    //> for field in type_def.fields:
        this.{{ field.java.name }} = {{ field.java.name }};
    //> endfor
    }

//> for field in type_def.fields:
    //? field.comment : field.java.comment | comment | indent
    //? field.deprecated : "@Deprecated"
    public {{ field.java.data_type }} {{ field.java.getter }}() { return {{ field.java.name }}; }
//> endfor
//> if 'eq' in type_def.deriving and type_def.fields:

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof {{ type_def.java.name }})) {
            return false;
        }
        {{ type_def.java.name }} other = ({{ type_def.java.name }}) obj;
        return
        /*>- for field in type_def.fields */
{{ (" " * 15 if not loop.first else " ") ~ field.java.equals ~ (";" if loop.last else " &&") }}
        /*> endfor */
    }

    @Override
    public int hashCode() {
        // Pick an arbitrary non-zero starting value
        int hashCode = 17;
        //> for field in type_def.fields:
        hashCode = hashCode * 31 + {{ field.java.hash_code }};
        //> endfor
        return hashCode;
    }
//> endif
//> if 'ord' in type_def.deriving and type_def.fields:

    @Override
    public int compareTo({{ type_def.java.name }} other) {
        int tempResult;
        //> for field in type_def.fields:
        //> if field.type_ref.type_def.java.typename == field.type_ref.type_def.java.boxed:
            tempResult = this.{{ field.java.name }}.compareTo(other.{{ field.java.name }});
        //> else:
            if (this.{{ field.java.name }} < other.{{ field.java.name }}) {
                tempResult = -1;
            } else if (this.{{ field.java.name }} > other.{{ field.java.name }}) {
                tempResult = 1;
            } else {
                tempResult = 0;
            }
        //> endif
        if (tempResult != 0) {
            return tempResult;
        }
        //> endfor
        return 0;
    }
//> endif
//> if config.string_serialization

    @Override
    public String toString() {
        return "{{ type_def.java.typename }}{" +
        //> for field in type_def.fields:
            "{{ ("," if not loop.first) ~ field.java.name }}=" + {{ field.java.name }} +
        //> endfor
        "}";
    }
//> endif
}
//> endblock
