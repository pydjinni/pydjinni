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

//> macro to_kotlin(type_ref):
//> if type_ref and type_ref.type_def.primitive == "interface":
{{ type_ref.type_def.java.name}}.of({{ caller() }})
//> else:
{{ caller() }}
//> endif
//> endmacro

/*> macro parameters(method) */
/*>- for parameter in method.parameters -*/
    {{ parameter.java.name ~ ((("?" if parameter.type_ref.optional) ~ ".delegate") if parameter.type_ref.type_def.primitive == "interface") ~ (", " if not loop.last) }}
/*>- endfor -*/
/*> endmacro */

//> block content
//> if type_def.methods | selectattr("asynchronous") | any
import kotlinx.coroutines.future.await
import kotlinx.coroutines.future.future
//> endif
{{ "" }}
interface {{ type_def.java.name }} {

    //> if "cpp" in type_def.targets
    companion object {
        fun of(delegate: {{ type_def.java.typename }}): {{ type_def.java.name }} {
            return {{ type_def.java.name }}Delegate(delegate)
        }
        @JvmName("ofOptional")
        fun of(delegate: {{ type_def.java.typename }}?): {{ type_def.java.name }}? {
            return delegate?.let { {{ type_def.java.name }}Delegate(it) }
        }
        //> for method in type_def.methods if method.static:
        {{ "suspend " if method.asynchronous }}fun {{ method.java.name }}(
            /*>- for parameter in method.parameters -*/
                {{ parameter.java.name }}: {{ parameter.kotlin.data_type ~ (", " if not loop.last) }}
            /*>- endfor -*/
        ): {{ method.kotlin.return_type }} {
            {{ "return " if method.return_type_ref }}/*> call to_kotlin(method.return_type_ref) */{{ type_def.java.typename }}.{{ method.java.name }}({{ parameters(method) }}){{ ".await()" if method.asynchronous }}/*> endcall */
        }
        //> endfor
    }
    //> endif

    val delegate: {{ type_def.java.typename }}
    //> if "java" in type_def.targets
        get() = object : {{ type_def.java.typename }}() {
            //> for method in type_def.methods if not method.static:
            override fun {{ method.java.name }}(
                /*>- for parameter in method.parameters -*/
                    {{ parameter.java.name }}: {{ parameter.kotlin.java_delegate_data_type ~ (", " if not loop.last) }}
                /*>- endfor -*/
            ): {{ method.kotlin.java_delegate_return_type }} {
                {{ ("return " if method.return_type_ref or method.asynchronous) ~ ("kotlinx.coroutines.GlobalScope.future { " if method.asynchronous) }}this@{{ type_def.java.name }}.{{ method.java.name }}(
                    /*>- for parameter in method.parameters -*/
                    {{ ( (parameter.java.typename ~ ".of(") if parameter.type_ref.type_def.primitive == "interface" ) ~ parameter.java.name ~ ( ")" if parameter.type_ref.type_def.primitive == "interface" ) ~ (", " if not loop.last) }}
                    /*>- endfor -*/
                ){{ (((("?" if method.return_type_ref.optional ) ~ ".delegate") if method.return_type_ref.type_def.primitive == "interface") if method.return_type_ref) ~ ((" }" ~ (".thenApply { null }" if not method.return_type_ref )) if method.asynchronous) }}
            }
            //> endfor
        }
    //> endif
    //> for method in type_def.methods if not method.static:
    {{ "suspend " if method.asynchronous }}fun {{ method.java.name }}(
    /*>- for parameter in method.parameters -*/
        {{ parameter.java.name }}: {{ parameter.kotlin.data_type ~ (", " if not loop.last) }}
    /*>- endfor -*/
    ): {{ method.kotlin.return_type }}
    //> endfor

    //> if "cpp" in type_def.targets
    class {{ type_def.java.name }}Delegate(override val delegate: {{ type_def.java.typename }}) : {{ type_def.java.name }} {
        //> for method in type_def.methods if not method.static:
        override {{ "suspend " if method.asynchronous }}fun {{ method.java.name }}(
        /*>- for parameter in method.parameters -*/
            {{ parameter.java.name }}: {{ parameter.kotlin.data_type ~ (", " if not loop.last) }}
        /*>- endfor -*/
        ): {{ method.kotlin.return_type }} {
            {{ "return " if method.return_type_ref }}/*> call to_kotlin(method.return_type_ref) */delegate.{{method.java.name}}({{ parameters(method) }}){{ ".await()" if method.asynchronous }}/*> endcall */
        }
        //> endfor

    }
    //> endif
}
//> endblock
