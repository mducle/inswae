set(SRC_FILES
    src/Atom.cpp
    src/AttenuationProfile.cpp
    src/Exception.cpp
    src/Interpolation.cpp
    src/Logger.cpp
    src/Material.cpp
    src/MaterialBuilder.cpp
    src/NeutronAtom.cpp
    src/Property.cpp
    src/PropertyHistory.cpp
    src/SingletonHolder.cpp
    src/Strings.cpp
    src/StringTokenizer.cpp
    src/ThreadSafeLogStream.cpp
    src/UnitLabel.cpp
)

add_library(Kernel OBJECT ${SRC_FILES})
target_include_directories(Kernel PRIVATE
    inc
    ../Types/inc
    ${Boost_INCLUDE_DIRS}
)
set_property(TARGET Kernel PROPERTY POSITION_INDEPENDENT_CODE ON)
