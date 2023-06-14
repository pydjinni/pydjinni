set(JAVA_AWT_LIBRARY NotNeeded)
set(JAVA_AWT_INCLUDE_PATH NotNeeded)
find_package(JNI REQUIRED)

add_subdirectory(jni/support_lib)

if(BUILD_TESTING)
    add_subdirectory(it)
endif()

