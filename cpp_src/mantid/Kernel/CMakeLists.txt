set(SRC_FILES
    src/Atom.cpp
    src/AttenuationProfile.cpp
    src/Exception.cpp
    src/Interpolation.cpp
    src/Logger.cpp
    src/Material.cpp
    src/MaterialBuilder.cpp
    src/NeutronAtom.cpp
    src/SingletonHolder.cpp
)

add_library(Kernel OBJECT ${SRC_FILES})
target_include_directories(Kernel PRIVATE inc ${Boost_INCLUDE_DIRS})
set_property(TARGET Kernel PROPERTY POSITION_INDEPENDENT_CODE ON)
