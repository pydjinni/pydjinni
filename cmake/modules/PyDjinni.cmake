# MIT License
#
# PyDjinni
# https://github.com/pydjinni/pydjinni
#
# Copyright (c) 2023 jothepro
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

cmake_minimum_required(VERSION 3.19)

function(pydjinni_generate IDL)
    cmake_parse_arguments(DJINNI
        # options
            "CLEAN"
        # one-value keywords
            "CONFIG;WORKING_DIRECTORY"
        # multi-value keywords
            "LANGUAGES;OPTIONS"
        # args
            ${ARGN}
    )

    set(MESSAGE_PREFIX "[pydjinni]")

    # find Djinni executable.
    find_program(DJINNI_EXECUTABLE pydjinni REQUIRED)
    # output djinni version
    execute_process(COMMAND ${DJINNI_EXECUTABLE} --version
        OUTPUT_STRIP_TRAILING_WHITESPACE
        OUTPUT_VARIABLE DJINNI_VERSION_OUTPUT)
    string(REGEX MATCH "version.*" VERSION "${DJINNI_VERSION_OUTPUT}")
    message(STATUS "${MESSAGE_PREFIX} ${VERSION}")

    set(DJINNI_PROCESSED_FILES_OUTFILE ${CMAKE_CURRENT_BINARY_DIR}/pydjinni/out/processed-files.json)
    list(JOIN DJINNI_LANGUAGES ", " DJINNI_LANGUAGES_STRING)
    message(STATUS "${MESSAGE_PREFIX} Generating Gluecode from '${IDL}' for target languages: ${DJINNI_LANGUAGES_STRING}")

    if(DJINNI_CLEAN)
        list(APPEND ADDITIONAL_GENERATE_OPTIONS --clean)
    endif()
    if(DJINNI_CONFIG)
        list(APPEND ADDITIONAL_OPTIONS --config ${DJINNI_CONFIG})
    endif()
    if(NOT DJINNI_WORKING_DIRECTORY)
        set(DJINNI_WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    endif()

    foreach(OPTION ${DJINNI_OPTIONS})
        list(APPEND ADDITIONAL_OPTIONS --option ${OPTION})
    endforeach()

    # generate c++ interface
   execute_process(COMMAND ${DJINNI_EXECUTABLE}
            ${ADDITIONAL_OPTIONS}
            --option generate.list_processed_files:${DJINNI_PROCESSED_FILES_OUTFILE}
            generate ${ADDITIONAL_GENERATE_OPTIONS} ${IDL} ${DJINNI_LANGUAGES}
        RESULT_VARIABLE PYDIJNNI_RESULT
        WORKING_DIRECTORY ${DJINNI_WORKING_DIRECTORY}
    )

    if(NOT PYDIJNNI_RESULT EQUAL 0)
        message(FATAL_ERROR "${MESSAGE_PREFIX} Error generating glue code (Error ${PYDIJNNI_RESULT})")
    endif()

    file(READ ${DJINNI_PROCESSED_FILES_OUTFILE} PROCESSED_FILES)

    # helper function that converts a JSON list to a CMake list
    function(json_to_list OUTPUT_LIST_VAR JSON_LIST)
        string(JSON LIST_LENGTH LENGTH ${JSON_LIST})
        if(${LIST_LENGTH} GREATER 0)
            math(EXPR STOP "${LIST_LENGTH} - 1")
            foreach(INDEX RANGE ${STOP})
                string(JSON ITEM GET ${JSON_LIST} ${INDEX})
                file(TO_CMAKE_PATH ${ITEM} CMAKE_PATH_ITEM)
                list(APPEND OUTPUT_LIST ${CMAKE_PATH_ITEM})
            endforeach()
            set(${OUTPUT_LIST_VAR} "${OUTPUT_LIST}" PARENT_SCOPE)
        endif()
    endfunction()

    function(print_list LEVEL LIST)
        list(APPEND CMAKE_MESSAGE_INDENT "    + ")
        foreach(ITEM IN ITEMS ${LIST})
        message(${LEVEL} "${ITEM}")
        endforeach()
        list(POP_BACK CMAKE_MESSAGE_INDENT)
    endfunction()

    function(get_generated_files LANGUAGE KEY)
        string(TOUPPER ${KEY} VAR_KEY)
        string(JSON GENERATED_JSON
            ERROR_VARIABLE GENERATED_JSON_ERROR
            GET ${PROCESSED_FILES} generated ${LANGUAGE} ${KEY})
        if(NOT GENERATED_JSON_ERROR)
            json_to_list(GENERATED_FILES ${GENERATED_JSON})
            set(${LANGUAGE}_GENERATED_${VAR_KEY}S ${GENERATED_FILES} PARENT_SCOPE)
            message(VERBOSE "${MESSAGE_PREFIX} set variable ${LANGUAGE}_GENERATED_${VAR_KEY}S")
            print_list(DEBUG "${GENERATED_FILES}")
        endif()
    endfunction()

    string(JSON PARSED_IDL_FILES_JSON GET ${PROCESSED_FILES} parsed idl)
    json_to_list(PARSED_IDL_FILES ${PARSED_IDL_FILES_JSON})
    message(VERBOSE "${MESSAGE_PREFIX} parsed IDL files:")
    print_list(VERBOSE "${PARSED_IDL_FILES}")

    string(JSON PARSED_EXTERNAL_TYPE_FILES_JSON GET ${PROCESSED_FILES} parsed external_types)
    json_to_list(PARSED_EXTERNAL_TYPE_FILES ${PARSED_EXTERNAL_TYPE_FILES_JSON})
    message(VERBOSE "${MESSAGE_PREFIX} parsed external types:")
    print_list(VERBOSE "${PARSED_EXTERNAL_TYPE_FILES}")

    string(JSON GENERATED_LANGUAGES_LENGTH LENGTH ${PROCESSED_FILES} generated)
    math(EXPR STOP "${GENERATED_LANGUAGES_LENGTH} - 1")
    foreach(INDEX RANGE ${STOP})
        string(JSON GENERATED_LANGUAGE_JSON MEMBER ${PROCESSED_FILES} generated ${INDEX})
        list(APPEND GENERATED_LANGUAGES ${GENERATED_LANGUAGE_JSON})
    endforeach()
    list(JOIN GENERATED_LANGUAGES ", " GENERATED_LANGUAGES_STRING)
    message(STATUS "${MESSAGE_PREFIX} successfully generated output for: ${GENERATED_LANGUAGES_STRING}")

    foreach(LANGUAGE ${GENERATED_LANGUAGES})
        get_generated_files(${LANGUAGE} header)
        set(${LANGUAGE}_GENERATED_HEADERS ${${LANGUAGE}_GENERATED_HEADERS} PARENT_SCOPE)
        get_generated_files(${LANGUAGE} source)
        set(${LANGUAGE}_GENERATED_SOURCES ${${LANGUAGE}_GENERATED_SOURCES} PARENT_SCOPE)
    endforeach()

    # trigger re-generation if IDL file or config changes
    list(APPEND DEPENDS ${PARSED_IDL_FILES})
    list(APPEND DEPENDS ${PARSED_EXTERNAL_TYPE_FILES})
    if(DJINNI_CONFIG AND NOT DJINNI_CONFIG STREQUAL "None")
        file(TO_CMAKE_PATH ${DJINNI_CONFIG} CMAKE_PATH_CONFIG)
        list(APPEND DEPENDS ${CMAKE_PATH_CONFIG})
    endif()
    message(DEBUG "${MESSAGE_PREFIX} CMAKE_CONFIGURE_DEPENDS:")
    print_list(DEBUG "${DEPENDS}")
    set_directory_properties(PROPERTIES CMAKE_CONFIGURE_DEPENDS "${DEPENDS}")
endfunction()
