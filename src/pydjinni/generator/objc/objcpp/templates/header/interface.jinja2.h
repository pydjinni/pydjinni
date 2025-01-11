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
/*> extends "base.jinja2" */

//> block global
{{ ("@protocol " if "objc" in type_def.targets else "@class ") ~ type_def.objc.typename }};
//> endblock

//> block content
class {{ type_def.cpp.deprecated ~ type_def.objcpp.name }} {
public:
    using CppType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using CppOptType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using ObjcType =
    /*>- if "objc" in type_def.targets -*/
        id<{{ type_def.objc.typename }}>;
    /*>- else -*/
        ::{{ type_def.objc.typename }}*;
    /*> endif */

    using Boxed = {{ type_def.objcpp.name }};

    static CppType toCpp(ObjcType objc);
    static ObjcType fromCppOpt(const CppOptType& cpp);
    static ObjcType fromCpp(const CppType& cpp) { return fromCppOpt(cpp); }

private:
    class ObjcProxy;
};
//> endblock
