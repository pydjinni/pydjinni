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
@FunctionalInterface
{{ type_def.java.class_modifier }}interface {{ type_def.java.name }} {
    //? type_def.java.nullable_annotation : type_def.java.nullable_annotation
    {{ type_def.java.return_type }} invoke({{ parameters(type_def) }});
}

//> if type_def.cpp.proxy:
final class {{ type_def.java.name }}CppProxy implements {{ type_def.java.name }} {
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

    private {{ type_def.java.name }}CppProxy(long nativeRef)
    {
        if (nativeRef == 0) throw new RuntimeException("nativeRef is zero");
        this.nativeRef = nativeRef;
        {{ native_cleaner.package }}.{{ native_cleaner.name }}.register(this, new CleanupTask(nativeRef));
    }

    @Override
    public {{ type_def.java.return_type }} invoke({{ parameters(type_def) }}) {
        {{ "return" if type_def.return_type_ref }} nativeInvoke(this.nativeRef{{ (", " if type_def.parameters) ~ parameters(type_def, with_types=False) }});
    }
    private native {{ type_def.java.return_type }} nativeInvoke(long _nativeRef{{ (", " if type_def.parameters) ~ parameters(type_def) }});
}
//> endif
//> endblock
