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

//> block global
//? type_def.objcpp.attributes : type_def.objcpp.attributes | join('\n')
@interface {{ type_def.objc.typename }}
    /*>- if "objc" in type_def.targets -*/
        CppProxy : NSObject<{{ type_def.objc.typename }}>
    /*>- else -*/
        ()
    /*> endif */

- (id)initWithCpp:(const std::shared_ptr<{{ type_def.cpp.typename }}>&)cppRef;
@end

@implementation {{ type_def.objc.typename ~ ("CppProxy" if "objc" in type_def.targets) }} {
    ::pydjinni::CppProxyCache::Handle<std::shared_ptr<{{ type_def.cpp.typename }}>> _cppRefHandle;
}

- (id)initWithCpp:(const std::shared_ptr<{{ type_def.cpp.typename }}>&)cppRef {
    if (self = [super init]) {
        _cppRefHandle.assign(cppRef);
    }
    return self;
}

//> for method in type_def.methods:
{{ method.objc.specifier }} ({{ method.objc.type_decl if not method.asynchronous else "void"}}){{ method.objc.name }}
    /*>- for parameter in method.objc.parameters -*/
    {{ ":" if loop.first else ( " " ~ parameter.name ~ ":") }}({{ (parameter.annotation ~ " ") if parameter.annotation }}{{ parameter.type_decl }}){{ parameter.name }}
    /*>- endfor -*/
    {
    //> call cpp_error_handling(method)
    //? method.deprecated : "PYDJINNI_DISABLE_DEPRECATED_WARNINGS"
    {{ "auto objcpp_result_ = " if (method.return_type_ref and not method.asynchronous) }}
    /*>- if method.static -*/
        {{ type_def.cpp.typename }}::
    /*>- else -*/
        _cppRefHandle.get()->
    /*>- endif -*/
    {{ method.cpp.name }}(
    /*>- for parameter in method.parameters -*/
        {{ parameter.objcpp.translator }}::toCpp({{ parameter.objc.name }}){{ ", " if not loop.last }}
    /*>- endfor -*/
    )
    /*>- if method.asynchronous -*/
    .on_success(
        [completion]({{ method.cpp.callback_type_spec ~ " objcpp_result_" if method.return_type_ref }}) -> void {
            completion(
            /*>- if method.return_type_ref -*/
                {{ method.objcpp.return_type_translator }}::fromCpp(objcpp_result_)
            /*>- endif -*/
            /*>- if not method.cpp.noexcept -*/
                {{ ", " if method.return_type_ref }}nil
            /*>- endif -*/
            );
        })/*> if not method.cpp.noexcept */.on_error([completion](const std::exception_ptr& e){
            try {
                std::rethrow_exception(e);
            }
            /*> if method.throwing */
            /*> for error_domain_ref in method.throwing */
            /*> set error_domain = error_domain_ref.type_def */
            /*> for error_code in error_domain.error_codes */
            catch (const {{ error_domain.cpp.typename }}::{{ error_code.cpp.name }}& e) {
                completion({{ "{}, " if method.return_type_ref }}{{ error_domain.objcpp.namespace }}::{{ error_domain.objcpp.name }}::fromCpp(e));
            }
            /*> endfor */
            /*> endfor */
            /*> endif */
            catch (const ::pydjinni::objc_exception& e) {
                completion({{ "{}, " if method.return_type_ref }}::pydjinni::objc_exception::fromCpp(e));
            }
            catch (const std::exception& e) {
                completion({{ "{}, " if method.return_type_ref }}::pydjinni::objc_exception::fromCpp(e));
            }
        })/*> endif */.run(pydjinni::coroutine::schedule::darwin)
    /*>- endif -*/
    ;
    //? method.deprecated : "PYDJINNI_ENABLE_WARNINGS"
    /*> if method.return_type_ref and not method.asynchronous */
    return {{ method.objcpp.return_type_translator }}::fromCpp(objcpp_result_);
    /*> endif */
    //> endcall
}
//> endfor

/*> if "objc" not in type_def.targets */
namespace {{ type_def.objcpp.namespace }} {

auto {{ type_def.objcpp.translator }}::toCpp(ObjcType objc) -> CppType {
        if(!objc) {
            return nullptr;
        }
        return objc->_cppRefHandle.get();
}
auto {{ type_def.objcpp.translator }}::fromCppOpt(const CppOptType& cpp) -> ObjcType {
        if(!cpp) {
            return nil;
        }
        return ::pydjinni::get_cpp_proxy<::{{ type_def.objc.typename }}>(cpp);
}

} // namespace {{ type_def.objcpp.namespace }}
/*> endif */
@end
//> endblock

//> block content
//> if "objc" in type_def.targets
class {{ type_def.objcpp.name }}::ObjcProxy final : public {{ type_def.cpp.typename }}, private ::pydjinni::ObjcProxyBase<ObjcType> {
    friend class {{ type_def.objcpp.translator }};
public:
    using ObjcProxyBase::ObjcProxyBase;
    //> for method in type_def.methods
    //? method.deprecated : "[[deprecated]]"
    {{ method.cpp.prefix_specifiers(implementation=True) ~ method.cpp.type_spec }} {{ method.cpp.name }}(
    /*>- for parameter in method.parameters -*/
        {{ parameter.cpp.type_spec }} {{ parameter.cpp.name}}{{ ", " if not loop.last }}
    /*>- endfor -*/
    ){{ method.cpp.postfix_specifiers(implementation=True) }} override {
        //> if method.asynchronous
        {{ "auto result = " if method.return_type_ref }}co_await pydjinni::coroutine::CallbackAwaitable<{{ method.return_type_ref.type_def.cpp.typename if method.return_type_ref else "void" }}> {
            [&](pydjinni::coroutine::CallbackHandle<{{ method.return_type_ref.type_def.cpp.typename if method.return_type_ref }}>& handle) -> void {
        //> endif
        @autoreleasepool {
            //> if not method.cpp.noexcept and not method.asynchronous
            NSError* error;
            //> endif
            {{ "auto objcpp_result_ = " if method.return_type_ref.type_def and not method.asynchronous }}[djinni_private_get_proxied_objc_object() {{ method.objc.name }}
            /*>- for parameter in method.parameters -*/
                {{ " " ~ parameter.objc.name if not loop.first }}:({{ parameter.objcpp.translator }}::fromCpp({{ parameter.cpp.name }}))
            /*>- endfor -*/
            /*>- if method.asynchronous -*/
            {{ " completion" if method.parameters }}:(^ ({{ ( method.objc.type_decl ~ " value") if method.return_type_ref }} {{ "NSError* error" if not method.cpp.noexcept }}){
                //> if not method.cpp.noexcept:
                if(error) {
                    //> if method.throwing:
                    /*> for error_domain_ref in method.throwing */
                    /*> set error_domain = error_domain_ref.type_def */
                    {{ "else " if not loop.first }}if(error.domain == {{ error_domain.objc.domain_name }}) {
                        handle.error(::{{ error_domain.objcpp.namespace }}::{{ error_domain.objcpp.name }}::toCpp(error));
                        return;
                    }
                    //> endfor
                    else {
                        handle.error(std::make_exception_ptr(::pydjinni::objc_exception::toCpp(error)));
                        return;
                    }
                    //> else:
                    handle.error(std::make_exception_ptr(::pydjinni::objc_exception::toCpp(error)));
                    return;
                    //> endif
                }
                //> endif
                handle.resume({{ (method.objcpp.return_type_translator ~ "::toCpp(value)") if method.return_type_ref }});
            })
            /*>- endif -*/
            {{- ":&error" if not method.cpp.noexcept and not method.asynchronous -}}
            ];
            {{ objc_error_handling(method) | indent(12) }}
            //> if method.return_type_ref.type_def and not method.asynchronous
            return {{ method.objcpp.return_type_translator }}::toCpp(objcpp_result_);
            //> endif
        }
        //> if method.asynchronous:
        }};
        //> if method.return_type_ref
        co_return result;
        //> endif
        //> endif
    }
    //> endfor
};

auto {{ type_def.objcpp.name }}::toCpp(ObjcType objc) -> CppType {
    if(!objc) {
        return nullptr;
    }
    return ::pydjinni::get_objc_proxy<ObjcProxy>(objc);
}

auto {{ type_def.objcpp.name }}::fromCppOpt(const CppOptType& cpp) -> ObjcType {
    if(!cpp) {
        return nil;
    }
    return dynamic_cast<ObjcProxy&>(*cpp).djinni_private_get_proxied_objc_object();
}
//> endif
//> endblock
