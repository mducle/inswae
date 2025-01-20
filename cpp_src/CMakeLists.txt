cmake_minimum_required (VERSION 3.15)
project(micromantid)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_MACOSX_RPATH TRUE)
set(CMAKE_CXX_STANDARD 20)
set(CXX_STANDARD_REQUIRED 20)
cmake_policy(SET CMP0167 NEW)
cmake_policy(SET CMP0148 OLD)  # New policy gives error when cannot find shared libs

set(MICROMANTID_PYTHON_MODULE micromantid)

if (DEFINED ENV{CONDA_PREFIX})
    message(STATUS "Searching $ENV{CONDA_PREFIX} for Pybind11 and Boost")
    file(GLOB pybind11_search $ENV{CONDA_PREFIX}/share/cmake/pybind11/pybind11Config.cmake)
    if (DEFINED pybind11_search)
        cmake_path(GET pybind11_search PARENT_PATH pybind11_DIR)
    endif()
    file(GLOB boost_search $ENV{CONDA_PREFIX}/lib/cmake/Boost-*/BoostConfig.cmake)
    if (DEFINED boost_search)
        cmake_path(GET boost_search PARENT_PATH Boost_DIR)
        string(REGEX MATCH "-[0-9]\.[0-9\.]*" boost_version ${Boost_DIR})
        string(CONCAT boost_headers_DIR "$ENV{CONDA_PREFIX}/lib/cmake/boost_headers" ${boost_version})
    endif()
endif()

if (EMSCRIPTEN)
    message(STATUS "Emscripten detected - setting Pybind to use cross-compiler")
    set(PYBIND11_USE_CROSSCOMPILING TRUE)
endif()

find_package(pybind11 CONFIG)
find_package(Boost)
find_package(Poco REQUIRED Foundation)

if (EMSCRIPTEN)
    # We can't use the provided Poco::Foundation label as it uses dynamic linking
    file(GLOB POCOLIB ${Poco_DIR}/../../libPocoFoundation.a)
    if (NOT POCOLIB)
        message(FATAL_ERROR "libPocoFoundation.a not found - please build and install Poco")
    endif()
else()
    set(POCOLIB "Poco::Foundation")
endif()

# Add the Pybind11 bindings
pybind11_add_module(${MICROMANTID_PYTHON_MODULE} MODULE)
target_include_directories(${MICROMANTID_PYTHON_MODULE} PUBLIC ${Boost_INCLUDE_DIRS} ${pybind11_INCLUDE_DIRS})

# Add the raw Mantid source files
add_subdirectory(mantid)

set(MICROMANTID_PYTHON_SOURCES
    micromantid.cpp   # This must be first
    ${MICROMANTID_KERNEL_BINDINGS}
)
target_sources(${MICROMANTID_PYTHON_MODULE} PRIVATE ${MICROMANTID_PYTHON_SOURCES})
target_link_libraries(${MICROMANTID_PYTHON_MODULE} PUBLIC ${MICROMANTID_CXX_LIBRARIES} ${POCOLIB})

# Destination name must match name of project in pyproject.toml
install(TARGETS ${MICROMANTID_PYTHON_MODULE} DESTINATION ${MICROMANTID_PYTHON_MODULE})
