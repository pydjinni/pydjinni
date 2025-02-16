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
{{ type_def.java.class_modifier }}abstract class {{ type_def.java.name }} {
    //> if type_def.main and config.native_lib:
    static {
        {{ native_lib_loader.package }}.{{ native_lib_loader.name }}.loadLibrary();
    }
    //> endif
    //> for method in type_def.methods:
    //? method.comment : method.java.comment | comment | indent
    //? method.deprecated : "@Deprecated"
    //? method.java.nullable_annotation : method.java.nullable_annotation
    public {{ "static" if method.static else "abstract" }} {{ method.java.return_type }} {{ method.java.name }}({{ parameters(method) }})
    /*>- if method.throwing -*/
        {{ " throws " }}
        /*>- for error in method.throwing -*/
            {{ error.type_def.java.name }}
        /*>- endfor -*/
    /*>- endif -*/
    /*>- if method.static -*/
    {
        {{ "return " if method.return_type_ref or method.asynchronous }}CppProxy.{{ method.java.name }}(
        /*>- for parameter in method.parameters -*/
        {{ parameter.java.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
        );
    };
    /*> else -*/
    ;
    //> endif
    //> endfor
    //> if type_def.cpp.proxy:
    private static final class CppProxy extends {{ type_def.java.name }} {
        private final long nativeRef;

        static class CleanupTask implements Runnable {
            private final long nativeRef;
            CleanupTask(long nativeRef) {
                this.nativeRef = nativeRef;
            }

            @Override
            public void run() {
                nativeDestroy(this.nativeRef);
            }

            private native void nativeDestroy(long nativeRef);
        }

        private CppProxy(long nativeRef) {
            if (nativeRef == 0) throw new RuntimeException("nativeRef is zero");
            this.nativeRef = nativeRef;
            {{ native_cleaner.package }}.{{ native_cleaner.name }}.register(this, new CleanupTask(nativeRef));
        }

        //> for method in type_def.methods:
        //> if method.static:
        public static native {{ method.java.return_type }} {{ method.java.name }}({{ parameters(method) }});
        //> else:
        @Override
        public {{ method.java.return_type }} {{ method.java.name }}({{ parameters(method) }}) {
            {{ "return " if method.return_type_ref or method.asynchronous -}} native_{{ method.java.name }}(this.nativeRef {{ (", " if method.parameters) ~ parameters(method, with_types=False) }});
        }
        private native {{ method.java.return_type }} native_{{ method.java.name }}(long _nativeRef{{ (", " if method.parameters) ~ parameters(method) }});
        //> endif
        //> endfor
    }
    //> endif
}
//> endblock
