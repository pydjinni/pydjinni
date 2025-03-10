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
//> if type_def.cppcli.base_type:
ref class {{ type_def.cppcli.derived_name }};
//> endif
//? type_def.cppcli.comment : type_def.cppcli.comment | comment
//? type_def.deprecated : type_def.cppcli.deprecated
public ref class {{ type_def.cppcli.name ~ (" sealed " if not type_def.cppcli.base_type else " abstract ") }}
    /*>- if 'eq' in type_def.deriving -*/
        : System::IEquatable<{{ type_def.cppcli.name }}^>
    /*>- endif *//*>- if 'ord' in type_def.deriving -*/
        {{ "," if 'eq' in type_def.deriving else ":" }} System::IComparable<{{ type_def.cppcli.name }}^>
    /*>- endif */ {
public:
    {{ type_def.cppcli.name }}(
    /*>- for field in type_def.fields -*/
        {{ field.cppcli.constructor_nullability_attribute ~ field.cppcli.typename }} {{ field.cppcli.name ~ (", " if not loop.last) }}
    /*>- endfor -*/
    );

    //> for field in type_def.fields:
    //? field.cppcli.comment : field.cppcli.comment | comment | indent
    //? field.deprecated : field.cppcli.deprecated
    //? field.cppcli.property_nullability_attribute : field.cppcli.property_nullability_attribute
    property {{ field.cppcli.typename }} {{ field.cppcli.property }}
    {
        {{ field.cppcli.typename }} get();
    }
    //> endfor
    //> if config.string_serialization:

    System::String^ ToString() override;
    //> endif
    //> if 'eq' in type_def.deriving:

    virtual bool Equals({{ type_def.cppcli.name }}^ other);
    bool Equals(System::Object^ obj) override;
    int GetHashCode() override;
    //> endif
    //> if 'ord' in type_def.deriving:

    virtual int CompareTo({{ type_def.cppcli.name }}^ other);
    //> endif
internal:
    //? type_def.deprecated : "#pragma warning(suppress : 4996)"
    using CppType = {{ type_def.cpp.typename }};
    using CsType = {{ type_def.cppcli.derived_name }}^;

    static CppType ToCpp(CsType cs);
    static CsType FromCpp(const CppType& cpp);
private:
    //> for field in type_def.fields:
    {{ field.cppcli.typename }} _{{ field.cppcli.name }};
    //> endfor
};
//> endblock
