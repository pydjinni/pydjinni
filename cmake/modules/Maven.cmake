# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
