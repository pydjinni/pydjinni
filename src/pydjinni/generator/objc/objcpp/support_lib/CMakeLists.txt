cmake_minimum_required(VERSION 3.6.0)

project(PyDjinniObjc_SupportLib OBJC OBJCXX)

add_library(objc_support_lib
        src/pydjinni/support.mm
        src/pydjinni/error.mm
        src/pydjinni/proxy_cache.mm
)

target_compile_options(objc_support_lib PUBLIC "-fobjc-arc")

target_include_directories(objc_support_lib PUBLIC include)

target_link_libraries(objc_support_lib PUBLIC support_lib::common)

add_library(support_lib::objc ALIAS objc_support_lib)