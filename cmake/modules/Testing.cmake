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

# Internal module for Unit-Testing public modules

macro(scenario TITLE)
    set(CMAKE_MESSAGE_INDENT "")
    message(STATUS "SCENARIO: ${TITLE}")
    set(CMAKE_MESSAGE_INDENT "  ")
endmacro()

macro(given TITLE)
    set(CMAKE_MESSAGE_INDENT "  ")
    message(STATUS "GIVEN: ${TITLE}")
    set(CMAKE_MESSAGE_INDENT "    ")
endmacro()

macro(when TITLE)
    set(CMAKE_MESSAGE_INDENT "    ")
    message(STATUS "WHEN: ${TITLE}")
    set(CMAKE_MESSAGE_INDENT "      ")
endmacro()

macro(then TITLE)
    set(CMAKE_MESSAGE_INDENT "      ")
    message(STATUS "THEN: ${TITLE}")
    set(CMAKE_MESSAGE_INDENT "        ")
endmacro()


function(assert)
    list(JOIN ARGN " " ARGN_STRING)
    if(${ARGN})
        message(STATUS "ASSERT: '${ARGN_STRING}'")
    else()
        message(FATAL_ERROR "ASSERT FAILED: '${ARGN_STRING}'")
    endif()
endfunction()

function(assert_in_list ITEM LIST)
    list(FIND ${LIST} "${ITEM}" INDEX)
    if(INDEX GREATER_EQUAL 0)
        message(STATUS "ASSERT: '${ITEM}' was found in list '${${LIST}}'")
    else()
        message(FATAL_ERROR "ASSERT FAILED: could not find '${ITEM}' in list '${${LIST}}'")
    endif()
endfunction()
