# Copyright 2025 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

project(PyDjinniIntegrationTestExternalTypes CXX)

pydjinni_generate(exported_types.pydjinni CLEAN
    LANGUAGES cpp java objc cppcli yaml
    CONFIG None
    OPTIONS
        generate.support_lib_sources=False
        generate.cpp.out.header=generated/export/include/cpp
        generate.cpp.out.source=generated/export/src/cpp
        generate.cpp.string_serialization=False
        generate.cpp.namespace=test::exported_types
        generate.java.out=../../java/it/java/external_types/generated/export/java
        generate.java.package=test.exported_types
        generate.jni.out.header=../../java/it/java/external_types/generated/export/include/jni
        generate.jni.out.source=../../java/it/java/external_types/generated/export/src/jni
        generate.jni.namespace=test::exported_types::jni
        generate.jni.identifier.file.prefix=marshal_
        generate.jni.identifier.file.style=snake_case
        generate.jni.loader=False
        generate.objc.type_prefix=EXT
        generate.objc.string_serialization=False
        generate.objc.out.header=../../objc/it/objc/external_types/generated/export/include/objc
        generate.objc.out.source=../../objc/it/objc/external_types/generated/export/src/objc
        generate.objc.swift.rename_interfaces=False
        generate.objcpp.namespace=test::exported_types::objcpp
        generate.objcpp.out.header=../../objc/it/objc/external_types/generated/export/include/objcpp
        generate.objcpp.out.source=../../objc/it/objc/external_types/generated/export/src/objcpp
        generate.cppcli.out.header=../../cppcli/it/external_types/generated/export/include/cppcli
        generate.cppcli.out.source=../../cppcli/it/external_types/generated/export/src/cppcli
        generate.cppcli.namespace=Test::ExportedTypes::CppCli
        generate.cppcli.nullability_attributes=false
        generate.yaml.out=generated/export/yaml
        generate.yaml.out_file=exported_types.yaml
)

define_test_case(ExternalTypesTest
    INTERFACE external_types.pydjinni
    OPTIONS
        generate.cpp.namespace=test::external_types
    SOURCES
        src/main_interface.cpp
    INCLUDE_DIRS
        generated/export/include/cpp
)
