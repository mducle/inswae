set(SRC_FILES
    src/Material.cpp
    src/MaterialBuilder.cpp
)

add_library(Kernel OBJECT ${SRC_FILES})
target_include_directories(Kernel PRIVATE inc ${Boost_INCLUDE_DIRS})
set_property(TARGET Kernel PROPERTY POSITION_INDEPENDENT_CODE ON)
