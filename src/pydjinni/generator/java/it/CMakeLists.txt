find_package(Java 1.8 REQUIRED)
include(UseJava)
include(Maven)

maven_add(junit-platform-console-standalone GROUP org.junit.platform VERSION 1.9.3)

add_subdirectory(java)
add_subdirectory(kotlin)
