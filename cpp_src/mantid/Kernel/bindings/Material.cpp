// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#include "MantidKernel/Material.h"
#include "MantidKernel/Atom.h"
#include "MantidKernel/NeutronAtom.h"
#include <numeric>
#include <tuple>
#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace pybind11::literals;
using Mantid::Kernel::Material;
using Mantid::PhysicalConstants::NeutronAtom;
using Mantid::PhysicalConstants::Atom;

namespace {
/**
 *
 * @param chemicalFormula the chemical formula of the material (compound)
 * @return a tuple consisting of a list of the elements and their proportions
 */
std::tuple<std::vector<std::shared_ptr<Atom> >, std::vector<int> > chemicalFormula(const Material &self) {
  std::vector<std::shared_ptr<Atom> > atoms;
  std::vector<int> numberAtoms;
  for (const auto &formulaUnit : self.chemicalFormula()) {
    atoms.push_back(formulaUnit.atom);
    numberAtoms.push_back(formulaUnit.multiplicity);
  }
  return std::make_tuple(atoms, numberAtoms);
}

bool toBool(const Material &self) {
  return (self.cohScatterXSection() != 0.) || (self.incohScatterXSection() != 0.) ||
         (self.totalScatterXSection() != 0.) || (self.absorbXSection() != 0.) || (self.cohScatterLength() != 0.) ||
         (self.incohScatterLength() != 0.) || (self.totalScatterLength() != 0.) ||
         (self.cohScatterLengthReal() != 0.) || (self.cohScatterLengthImg() != 0.) ||
         (self.incohScatterLengthReal() != 0.) || (self.incohScatterLengthImg() != 0.) ||
         (self.cohScatterLengthSqrd() != 0.) || (self.incohScatterLengthSqrd() != 0.) ||
         (self.totalScatterLengthSqrd() != 0.);
}

/**
 *
 * @param rmm the relative molecular (formula) mass of this material
 * @return the relative molecular mass
 */
double relativeMolecularMass(const Material &self) {
  const auto &formula = self.chemicalFormula();
  return std::accumulate(formula.cbegin(), formula.cend(), 0., [](double sum, const auto &formulaUnit) {
    return sum + formulaUnit.atom->mass * formulaUnit.multiplicity;
  });
}
} // namespace

void export_Material(py::module &m) {
  py::class_<Material>(m, "Material")
      .def("name", &Material::name, py::return_value_policy::reference, "Name of the material")
      .def_property_readonly("numberDensity", &Material::numberDensity, "Number density in atoms per A^-3")
      .def_property_readonly("numberDensityEffective", &Material::numberDensityEffective, "Effective number density in atoms per A^-3")
      .def_property_readonly("packingFraction", &Material::packingFraction, "Packing fraction as a number, ideally, 0 to 1")
      .def_property_readonly("temperature", &Material::temperature, "Temperature")
      .def_property_readonly("pressure", &Material::pressure, "Pressure")
      .def_property_readonly("totalAtoms", &Material::totalAtoms, "Total number of atoms")
      .def("__bool__", &toBool, "Returns True if any of the scattering values are non-zero")
      .def("cohScatterXSection", &Material::cohScatterXSection,
           "Coherent Scattering Cross-Section for the given wavelength in barns")
      .def("incohScatterXSection", &Material::incohScatterXSection,
           "Incoherent Scattering Cross-Section for the given wavelength in barns")
      .def("totalScatterXSection", &Material::totalScatterXSection,
           "Total Scattering Cross-Section for the given wavelength in barns")
      .def("absorbXSection", &Material::absorbXSection, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Absorption Cross-Section for the given wavelength in barns")
      .def("cohScatterLength", &Material::cohScatterLength, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Coherent Scattering Length for the given wavelength in fm")
      .def("incohScatterLength", &Material::incohScatterLength, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Incoherent Scattering Length for the given wavelength in fm")
      .def("totalScatterLength", &Material::totalScatterLength, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Total Scattering Length for the given wavelength in fm")
      .def("cohScatterLengthReal", &Material::cohScatterLengthReal, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Real part of Coherent Scattering Length for the given wavelength in fm")
      .def("cohScatterLengthImg", &Material::cohScatterLengthImg, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Imaginary part of Coherent Scattering Length for the given wavelength in fm")
      .def("incohScatterLengthReal", &Material::incohScatterLengthReal, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Real part of Incoherent Scattering Length for the given wavelength in fm")
      .def("incohScatterLengthImg", &Material::incohScatterLengthImg, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Imaginary part of Incoherent Scattering Length for the given wavelength in fm")
      .def("cohScatterLengthSqrd", &Material::cohScatterLengthSqrd, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Coherent Scattering Length Squared <b>^2 for the given wavelength in fm^2")
      .def("incohScatterLengthSqrd", &Material::incohScatterLengthSqrd, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Incoherent Scattering Length Squared <b>^2 for the given wavelength in fm^2")
      .def("totalScatterLengthSqrd", &Material::totalScatterLengthSqrd, py::arg("lambda") = static_cast<double>(NeutronAtom::ReferenceLambda),
           "Total Scattering Length Squared <b^2> for the given wavelength in fm^2")
      .def("chemicalFormula", &chemicalFormula,
           "Chemical formula as a tuple of two lists: the first one contains the Atom object the second their multiplicities within the formula.")
      .def("relativeMolecularMass", &relativeMolecularMass, "Relative Molecular Mass");
}
