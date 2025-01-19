#include "MantidKernel/MaterialBuilder.h"
#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace pybind11::literals;
using namespace Mantid::Kernel;

void export_MaterialBuilder(py::module &m) {
  py::enum_<MaterialBuilder::NumberDensityUnit>(m, "NumberDensityUnit")
      .value("Atoms", MaterialBuilder::NumberDensityUnit::Atoms)
      .value("FormulaUnits", MaterialBuilder::NumberDensityUnit::FormulaUnits);

  py::class_<MaterialBuilder>(m, "MaterialBuilder")
      .def(py::init<>())
      .def("setName", &MaterialBuilder::setName, py::arg("name"),
           "Set the string name given to the material. Defaults to the chemical formula.")
      .def("setFormula", &MaterialBuilder::setFormula, py::arg("formula"),
           "Set the chemical formula of the material")
      .def("setAtomicNumber", &MaterialBuilder::setAtomicNumber, py::arg("atomicNumber"),
           "Set the atomic number of the material")
      .def("setMassNumber", &MaterialBuilder::setMassNumber, py::arg("massNumber"),
           "Set the mass number of the material")
      .def("setNumberDensity", &MaterialBuilder::setNumberDensity, py::arg("rho"),
           "Set the number density of the material in atoms (default) or formula units per Angstrom^3")
      .def("setPackingFraction", &MaterialBuilder::setPackingFraction, py::arg("fraction"),
           "Set the packing fraction of the material (default is 1). This is used to infer the effective number density.")
      .def("setNumberDensityUnit", &MaterialBuilder::setNumberDensityUnit, py::arg("unit"),
           "Change the number density units from atoms per Angstrom^3 to the desired unit")
      .def("setZParameter", &MaterialBuilder::setZParameter, py::arg("zparam"),
           "Set the number of formula units in a unit cell")
      .def("setUnitCellVolume", &MaterialBuilder::setUnitCellVolume, py::arg("cellVolume"),
           "Set the unit cell volume of the material")
      .def("setMassDensity", &MaterialBuilder::setMassDensity, py::arg("massDensity"),
           "Set the mass density of the material in g / cc")
      .def("setTotalScatterXSection", &MaterialBuilder::setTotalScatterXSection,
           py::arg("xsec"), "Set the total scattering cross section of the material in barns")
      .def("setCoherentXSection", &MaterialBuilder::setCoherentXSection, py::arg("xsec"),
           "Set the coherent cross section of the material in barns")
      .def("setIncoherentXSection", &MaterialBuilder::setIncoherentXSection,
           py::arg("xsec"), "Set the incoherent cross section of the material in barns")
      .def("setAbsorptionXSection", &MaterialBuilder::setAbsorptionXSection,
           py::arg("xsec"), "Set the absorption cross section of the material in barns")
      .def("build", &MaterialBuilder::build, py::return_value_policy::copy,
           "Build the new mantid.kernel.Material object from the current set of options");
}
