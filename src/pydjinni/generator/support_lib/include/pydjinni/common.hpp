#pragma once

#ifdef _MSC_VER
    #define DJINNI_WEAK_DEFINITION // weak attribute not supported by MSVC
    #define DJINNI_NORETURN_DEFINITION __declspec(noreturn)
    #if _MSC_VER < 1900 // snprintf not implemented prior to VS2015
        #define DJINNI_SNPRINTF snprintf
        #define noexcept _NOEXCEPT // work-around for missing noexcept VS2015
        #define constexpr // work-around for missing constexpr VS2015
    #else
        #define DJINNI_SNPRINTF _snprintf
    #endif
#else
    #define DJINNI_WEAK_DEFINITION __attribute__((weak))
    #define DJINNI_NORETURN_DEFINITION __attribute__((noreturn))
    #define DJINNI_SNPRINTF snprintf
#endif
