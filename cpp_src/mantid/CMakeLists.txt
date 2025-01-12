add_subdirectory(Kernel)

add_library(Kernel_bind OBJECT kernel_bind.cpp)
target_include_directories(Kernel_bind PRIVATE Kernel/inc ${Boost_INCLUDE_DIRS} ${pybind11_INCLUDE_DIRS})
set_property(TARGET Kernel_bind PROPERTY POSITION_INDEPENDENT_CODE ON)

set(LIBMANTID_CXX_LIBRARIES
    Kernel
    Kernel_bind
CACHE INTERNAL "")
