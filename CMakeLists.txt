cmake_minimum_required(VERSION 2.8.8)
project(segyviewer)

if (POLICY CMP0042)
    cmake_policy(SET CMP0042 NEW)
endif ()

include(${CMAKE_SOURCE_DIR}/cmake/python.cmake)

if (NOT DEFINED PYTHON_EXECUTABLE)
    message(FATAL_ERROR "Python interpreter not found! Unable to build!")
endif()

enable_testing()

if (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/install" CACHE PATH "Default install path" FORCE)
endif ()

add_subdirectory(src)
add_subdirectory(applications)
add_subdirectory(examples)
add_subdirectory(tests)
add_subdirectory(resources)
