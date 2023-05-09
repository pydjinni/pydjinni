project(PyDjinniIntegrationTests C CXX)

include(Maven)

maven_add(junit-jupiter-api GROUP org.junit.jupiter VERSION 5.9.3)
maven_add(apiguardian-api GROUP org.apiguardian VERSION 1.1.2)
maven_add(junit-platform-commons GROUP org.junit.platform VERSION 1.9.3)


add_subdirectory(record)
