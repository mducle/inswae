include(GenerateExportHeader)

set(SRC_FILES
    src/napi.cpp
    src/napi4.cpp
    src/napi5.cpp
    src/NeXusException.cpp
    src/NeXusFile.cpp
    src/nxstack.cpp
    src/stptok.cpp
)

set(INC_FILES
    inc/MantidNexusCpp/napi.h
    inc/MantidNexusCpp/napi4.h
    inc/MantidNexusCpp/napi5.h
    inc/MantidNexusCpp/napiconfig.h
    inc/MantidNexusCpp/napi_internal.h
    inc/MantidNexusCpp/NeXusException.hpp
    inc/MantidNexusCpp/NeXusFile.hpp
    inc/MantidNexusCpp/nx_stptok.h
    inc/MantidNexusCpp/nxstack.h
)

# Add the target for this directory
add_library(NexusCpp ${SRC_FILES} ${INC_FILES})
add_library(Mantid::NexusCpp ALIAS NexusCpp)

target_include_directories(
  NexusCpp PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/inc> $<INSTALL_INTERFACE:include/Mantid>
)

# Set the name of the generated library
set_target_properties(
  NexusCpp
  PROPERTIES OUTPUT_NAME MantidNexusCpp
             COMPILE_DEFINITIONS IN_MANTID_NEXUSCPP
             WITH_HDF4 WITH_HDF5
)
# H5_BUILT_AS_DYNAMIC_LIB required https://github.com/conda-forge/hdf5-feedstock/issues/58
target_compile_definitions(NexusCpp PUBLIC -DH5_BUILT_AS_DYNAMIC_LIB)
target_link_libraries(NexusCpp PUBLIC ${HDF4_DF_LIBRARY} ${HDF4_MFHDF_LIBRARY} ${HDF5_LIBRARIES} ${HDF5_HL_LIBRARIES})

if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
  set_target_properties(NexusCpp PROPERTIES INSTALL_RPATH "@loader_path/../MacOS;@loader_path/../Frameworks")
elseif(${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
  set_target_properties(NexusCpp PROPERTIES INSTALL_RPATH "\$ORIGIN/../${LIB_DIR}")
endif()

# Add to the 'Framework' group in VS
set_property(TARGET NexusCpp PROPERTY FOLDER "MantidFramework")

# Auto-generate exports header
target_include_directories(
  NexusCpp PUBLIC $<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/Framework/NexusCpp> $<INSTALL_INTERFACE:include/Mantid>
)
generate_mantid_export_header(NexusCpp FALSE)

# ######### Installation settings
set(TARGET_EXPORT_NAME "MantidNexusCppTargets")
mtd_install_framework_lib(TARGETS NexusCpp INSTALL_EXPORT_FILE EXPORT_NAME ${TARGET_EXPORT_NAME})
