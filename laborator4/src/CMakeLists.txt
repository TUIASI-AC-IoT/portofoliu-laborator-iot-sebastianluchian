# This file was automatically generated for projects
# without default 'CMakeLists.txt' file.
list(APPEND EXTRA_COMPONENT_DIRS mdns)
FILE(GLOB_RECURSE app_sources ${CMAKE_SOURCE_DIR}/src/*.*)

idf_component_register(SRCS ${app_sources})
