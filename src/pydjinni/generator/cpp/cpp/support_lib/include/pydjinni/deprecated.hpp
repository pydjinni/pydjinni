#pragma once

#ifdef _MSC_VER
    #define PYDJINNI_DISABLE_DEPRECATED_WARNINGS __pragma(warning(push)) __pragma(warning(disable: 4996 4947))
    #define PYDJINNI_ENABLE_WARNINGS __pragma(warning(pop))
#elif defined(__clang__)
    #define PYDJINNI_DISABLE_DEPRECATED_WARNINGS _Pragma("clang diagnostic push") _Pragma("clang diagnostic ignored \"-Wdeprecated-declarations\"")
    #define PYDJINNI_ENABLE_WARNINGS _Pragma("clang diagnostic pop")
#elif defined(__GNUC__)
    #define PYDJINNI_DISABLE_DEPRECATED_WARNINGS _Pragma("GCC diagnostic push") _Pragma("GCC diagnostic ignored \"-Wdeprecated-declarations\"")
    #define PYDJINNI_ENABLE_WARNINGS _Pragma("GCC diagnostic pop")
#else
    #define PYDJINNI_DISABLE_DEPRECATED_WARNINGS
    #define PYDJINNI_ENABLE_WARNINGS
#endif
