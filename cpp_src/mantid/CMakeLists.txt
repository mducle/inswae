add_subdirectory(Kernel)

target_include_directories(${MICROMANTID_PYTHON_MODULE} PUBLIC Kernel/inc Types/inc)

set(MICROMANTID_CXX_LIBRARIES
    Kernel
CACHE INTERNAL "")

set(MICROMANTID_KERNEL_BINDINGS
    mantid/kernel_bind.cpp
    mantid/Kernel/bindings/Material.cpp
    mantid/Kernel/bindings/MaterialBuilder.cpp
    mantid/Kernel/bindings/Property.cpp
CACHE INTERNAL "")
