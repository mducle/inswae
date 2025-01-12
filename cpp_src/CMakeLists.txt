cmake_minimum_required (VERSION 3.15)
project(libMantid)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_MACOSX_RPATH TRUE)
set(CMAKE_CXX_STANDARD 17)
set(CXX_STANDARD_REQUIRED 17)

set(LIBMANTID_PYTHON_MODULE libmantid)

#include(Eigen)
#include_directories(${EIGEN3_INCLUDE_DIR})

#include(PyBind11)
#add_subdirectory(${PyBind11_DIR})
find_package(pybind11 CONFIG)
find_package(Boost)

# Add the raw Mantid source files
add_subdirectory(mantid)

# Add the Pybind11 bindings
pybind11_add_module(${LIBMANTID_PYTHON_MODULE} MODULE)
target_include_directories(${LIBMANTID_PYTHON_MODULE} PUBLIC libmantid/include)

set(LIBMANTID_PYTHON_SOURCES
    libmantid.cpp   # This must be first
)
target_sources(${LIBMANTID_PYTHON_MODULE} PRIVATE ${LIBMANTID_PYTHON_SOURCES})
target_link_libraries(${LIBMANTID_PYTHON_MODULE} PUBLIC ${LIBMANTID_CXX_LIBRARIES})
