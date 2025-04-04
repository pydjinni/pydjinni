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
//? type_def.deprecated or type_def.fields | map(attribute="deprecated") | any : "#pragma warning(disable : 4947 4996)"
{{ type_def.cppcli.name }}::{{ type_def.cppcli.name }}(
/*>- for field in type_def.fields -*/
    {{ field.cppcli.typename }} {{ field.cppcli.name ~ (", " if not loop.last)}}
/*>- endfor -*/
)
//> for field in type_def.fields:
{{ ":" if loop.first else "," }} _{{ field.cppcli.name }}({{ field.cppcli.name }})
//> endfor
{}

//> for field in type_def.fields:
{{ field.cppcli.typename }} {{ type_def.cppcli.name }}::{{ field.cppcli.property }}::get()
{
    return _{{ field.cppcli.name }};
}
//> endfor

{{ type_def.cppcli.name }}::CppType {{ type_def.cppcli.name }}::ToCpp({{ type_def.cppcli.name }}::CsType cs)
{
    ASSERT(cs != nullptr);
    return {
    //> for field in type_def.fields:
        {{ field.cppcli.translator }}::ToCpp(cs->{{ field.cppcli.property }}){{ "," if not loop.last }}
    //> endfor
    };
}

{{ type_def.cppcli.name }}::CsType {{ type_def.cppcli.name }}::FromCpp(const {{ type_def.cppcli.name }}::CppType& cpp)
{
    return gcnew {{ type_def.cppcli.derived_name }}(
    //> for field in type_def.fields:
        {{ field.cppcli.translator }}::FromCpp(cpp.{{ field.cpp.name }}){{ "," if not loop.last }}
    //> endfor
    );
}
//> if 'eq' in type_def.deriving:

bool {{ type_def.cppcli.name }}::Equals({{ type_def.cppcli.name }}^ other)
{
    if (ReferenceEquals(nullptr, other)) return false;
    if (ReferenceEquals(this, other)) return true;
    return
    /*>- for field in type_def.fields */
{{ " " if loop.first else " " * 11 }}{{ field.cppcli.equals ~ (";" if loop.last else " &&") }}
    /*> endfor */
}

bool {{ type_def.cppcli.name }}::Equals(System::Object^ other)
{
    if (ReferenceEquals(nullptr, other)) return false;
    if (ReferenceEquals(this, other)) return true;
    return other->GetType() == GetType() && Equals(({{ type_def.cppcli.name }}^) other);
}

int {{ type_def.cppcli.name }}::GetHashCode()
{
    //> for field in type_def.fields:
    {{ "auto " if loop.first }}hashCode = {{ ("(hashCode * 397) ^ " if not loop.first) ~ field.cppcli.property ~ ("->" if field.type_ref.type_def.cppcli.reference else ".") }}GetHashCode();
    //> endfor
    return hashCode;
}
//> endif
//>  if 'ord' in type_def.deriving:

int {{ type_def.cppcli.name }}::CompareTo({{ type_def.cppcli.name }}^ other)
{
    if (ReferenceEquals(this, other)) return 0;
    if (ReferenceEquals(nullptr, other)) return 1;
    //> for field in type_def.fields:
    {{ "auto " if loop.first }}testComparison = {{ field.cppcli.compare }};
    if (testComparison != 0) return testComparison;
    //> endfor
    return 0;
}
//> endif
//> if config.string_serialization:

System::String^ {{ type_def.cppcli.name }}::ToString()
{
    return System::String::Format("{{ type_def.cppcli.cs_typename }}(
    /*>- for field in type_def.fields -*/
        {{ field.cppcli.property }}={ {{- loop.index - 1 -}} }{{ ", " if not loop.last }}
    /*>- endfor -*/
    )",
    //> for field in type_def.fields:
        {{ field.cppcli.property }}{{ "," if not loop.last}}
    //> endfor
    );
}
//> endif
//> endblock
