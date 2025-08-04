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
    //> for property in type_def.properties:
    private {{ property.java.data_type }} _{{ property.java.name }};
    private {{ property.java.signal_type }} _{{ property.java.name }}Signal = new {{ property.java.signal_type }}();
    //> endfor
    //> for method in type_def.methods:
    //? method.comment : method.java.comment | comment | indent
    //? method.deprecated : "@Deprecated"
    public {{ "static" if method.static else "abstract" }} {{ method.java.return_type }} {{ method.java.name }}({{ parameters(method) }})
    /*>- if method.throwing and not method.asynchronous -*/
        {{ " throws " }}
        /*>- for error in method.throwing -*/
            {{ error.type_def.java.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
    /*>- endif -*/
    /*>- if method.static */ {
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
    //> for property in type_def.properties:
    //? property.comment : property.java.comment | comment | indent
    //? property.deprecated : "@Deprecated"
    public {{ property.java.data_type }} {{ property.java.getter }}() {
        return _{{ property.java.name }};
    }
    //? property.deprecated : "@Deprecated"
    public {{ property.java.connection_type }} {{ property.java.notifier }}({{ property.java.callback_type }} callback) {
        return _{{ property.java.name }}Signal.connect(callback);
    };
    //? property.comment : property.java.comment | comment | indent
    //? property.deprecated : "@Deprecated"
    {{ "protected" if property.readonly else "public" }} void {{ property.java.setter }}({{ property.java.data_type }} value) {
        _{{ property.java.name }} = value;
        _{{ property.java.name }}Signal.notify(_{{ property.java.name }});
    };
    //> endfor
    //> if type_def.cpp.proxy:
    private static final class CppProxy extends {{ type_def.java.name }} {
        private final long nativeRef;

        //> for property in type_def.properties:
        private {{ property.java.connection_type }} {{ property.java.name }}Connection;
        //> endfor
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

        //> for property in type_def.properties:
        private void lazyInit{{ property.java.name }}() {
            if({{ property.java.name }}Connection == null) {
                {{ property.java.name }}Connection = native_{{ property.java.notifier }}(this.nativeRef, (newValue) -> {
                    super.{{ property.java.setter }}(newValue);
                });
                super.{{ property.java.setter }}(this.native_{{ property.java.getter }}(this.nativeRef));
            }
        }

        @Override
        public {{ property.java.data_type }} {{ property.java.getter }}() {
            lazyInit{{ property.java.name }}();
            return super.{{ property.java.getter }}();
        }

        private native {{ property.java.data_type }} native_{{ property.java.getter }}(long _nativeRef);

        @Override
        public {{ property.java.connection_type }} {{ property.java.notifier }}({{ property.java.callback_type }} callback) {
            lazyInit{{ property.java.name }}();
            return super.{{ property.java.notifier }}(callback);
        }

        private native {{ property.java.connection_type }} native_{{ property.java.notifier }}(long _nativeRef, {{ property.java.callback_type }} callback);

        //> if not property.readonly:
        @Override
        public void {{ property.java.setter }}({{ property.java.data_type }} value) {
            lazyInit{{ property.java.name }}();
            native_{{ property.java.setter }}(this.nativeRef, value);
        }

        private native void native_{{ property.java.setter }}(long _nativeRef, {{ property.java.data_type }} value);
        //> endif
        //> endfor

        //> for method in type_def.methods:
        //> if method.static:
        public static native {{ method.java.return_type }} {{ method.java.name }}({{ parameters(method) }});
        //> else:
        @Override
        public {{ method.java.return_type }} {{ method.java.name }}({{ parameters(method) }}) {
            {{ "return " if method.return_type_ref or method.asynchronous -}} native_{{ method.java.name }}(this.nativeRef{{ (", " if method.parameters) ~ parameters(method, with_types=False) }});
        }
        private native {{ method.java.return_type }} native_{{ method.java.name }}(long _nativeRef{{ (", " if method.parameters) ~ parameters(method) }});
        //> endif
        //> endfor
    }
    //> endif
}
//> endblock
