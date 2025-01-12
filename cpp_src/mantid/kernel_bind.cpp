#include "MantidKernel/MaterialBuilder.h"
#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace pybind11::literals;
using namespace Mantid::Kernel;

void wrap_kernel(py::module &m) {
    py::class_<MaterialBuilder>(m, "MaterialBuilder")
        .def(py::init<>())
        .def("setName", &MaterialBuilder::setName)
        .def("setFormula", &MaterialBuilder::setFormula)
        .def("setAtomicNumber", &MaterialBuilder::setAtomicNumber)
        .def("setMassNumber", &MaterialBuilder::setMassNumber)
        .def("setNumberDensity", &MaterialBuilder::setNumberDensity)
        .def("setNumberDensityUnit", &MaterialBuilder::setNumberDensityUnit)
        .def("setEffectiveNumberDensity", &MaterialBuilder::setEffectiveNumberDensity)
        .def("setPackingFraction", &MaterialBuilder::setPackingFraction)
        .def("setZParameter", &MaterialBuilder::setZParameter)
        .def("setUnitCellVolume", &MaterialBuilder::setUnitCellVolume)
        .def("setMassDensity", &MaterialBuilder::setMassDensity)
        .def("setTotalScatterXSection", &MaterialBuilder::setTotalScatterXSection)
        .def("setCoherentXSection", &MaterialBuilder::setCoherentXSection)
        .def("setIncoherentXSection", &MaterialBuilder::setIncoherentXSection)
        .def("setAbsorptionXSection", &MaterialBuilder::setAbsorptionXSection)
        .def("setAttenuationProfileFilename", &MaterialBuilder::setAttenuationProfileFilename)
        .def("setXRayAttenuationProfileFilename", &MaterialBuilder::setXRayAttenuationProfileFilename)
        .def("setAttenuationSearchPath", &MaterialBuilder::setAttenuationSearchPath)
        .def("build", &MaterialBuilder::build);
}
