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
