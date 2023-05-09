function(maven_add ARTIFACT_ID)

cmake_parse_arguments(MVN
        # options
            ""
        # one-value keywords
            "GROUP;VERSION"
        # multi-value keywords
            ""
        # args
            ${ARGN}
    )

string(REPLACE "." "/" MVN_GROUP_PATH ${MVN_GROUP})

FetchContent_Declare(
  ${ARTIFACT_ID}
  URL      https://repo1.maven.org/maven2/${MVN_GROUP_PATH}/${ARTIFACT_ID}/${MVN_VERSION}/${ARTIFACT_ID}-${MVN_VERSION}.jar
  DOWNLOAD_NO_EXTRACT TRUE
)

FetchContent_MakeAvailable(${ARTIFACT_ID})

find_jar(JAR_PATH ${ARTIFACT_ID} VERSIONS ${MVN_VERSION} PATHS ${${ARTIFACT_ID}_SOURCE_DIR})

set(${ARTIFACT_ID}_JAR ${JAR_PATH} PARENT_SCOPE)

endfunction()
