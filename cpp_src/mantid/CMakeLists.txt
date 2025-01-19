add_subdirectory(Kernel)

target_include_directories(${LIBMANTID_PYTHON_MODULE} PUBLIC Kernel/inc)

set(LIBMANTID_CXX_LIBRARIES
    Kernel
CACHE INTERNAL "")

set(LIBMANTID_KERNEL_BINDINGS
    mantid/kernel_bind.cpp
    mantid/Kernel/bindings/Material.cpp
    mantid/Kernel/bindings/MaterialBuilder.cpp
CACHE INTERNAL "")
