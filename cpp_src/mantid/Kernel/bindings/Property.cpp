#include "MantidKernel/Property.h"
#include <pybind11/pybind11.h>

namespace py = pybind11;
using Mantid::Kernel::Direction;

void export_Property(py::module &m) {
    py::enum_<Direction::Type>(m, "Direction")
        .value("Input", Direction::Input)
        .value("Output", Direction::Output)
        .value("InOut", Direction::InOut)
        .value("None", Direction::None);
}
