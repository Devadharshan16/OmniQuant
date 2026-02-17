cmake_minimum_required(VERSION 3.15)
project(OmniQuant VERSION 2.0 LANGUAGES CXX)

# C++17 Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optimization flags
if(MSVC)
    add_compile_options(/O2 /W4)
else()
    add_compile_options(-O3 -Wall -Wextra)
endif()

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Add pybind11
add_subdirectory(external/pybind11)

# Core library sources
set(CORE_SOURCES
    core/graph_engine.cpp
    core/cycle_detector.cpp
    core/edge_pruner.cpp
)

# Create shared library
add_library(omniquant_core STATIC ${CORE_SOURCES})

target_include_directories(omniquant_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

# Python module
pybind11_add_module(omniquant_cpp bindings/py_bindings.cpp)

target_link_libraries(omniquant_cpp PRIVATE omniquant_core)

# Install
install(TARGETS omniquant_cpp LIBRARY DESTINATION .)
