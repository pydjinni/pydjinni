project(PyDjinniIntegrationTests C CXX)


if(PYDJINNI_JNI)

find_package(Java 1.8 REQUIRED)
include(UseJava)
find_package(JNI REQUIRED)

include(Maven)

maven_add(junit-jupiter-api GROUP org.junit.jupiter VERSION 5.9.3)
maven_add(apiguardian-api GROUP org.apiguardian VERSION 1.1.2)
maven_add(junit-platform-commons GROUP org.junit.platform VERSION 1.9.3)

endif()
add_subdirectory(record)
