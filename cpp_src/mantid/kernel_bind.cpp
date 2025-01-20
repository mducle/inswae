#include "MantidKernel/MaterialBuilder.h"
#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace pybind11::literals;
using namespace Mantid::Kernel;

void export_Material(py::module &m);
void export_MaterialBuilder(py::module &m);
void export_Property(py::module &m);

void wrap_kernel(py::module &m) {
    auto m_kernel = m.def_submodule("kernel");
    export_Material(m_kernel);
    export_MaterialBuilder(m_kernel);
    export_Property(m_kernel);
}
