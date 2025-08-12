# This file was automatically generated for projects
# without default 'CMakeLists.txt' file.

# Declare C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Manually include .cpp and .c files, not headers
file(GLOB_RECURSE app_sources 
    ${CMAKE_CURRENT_SOURCE_DIR}/*.c
    ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp
)

idf_component_register(SRCS ${app_sources}
                       INCLUDE_DIRS ".")
