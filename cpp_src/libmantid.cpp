
#include <pybind11/pybind11.h>

namespace py = pybind11;

void wrap_kernel(py::module &);

PYBIND11_MODULE(libmcphase, m) {
    m.doc() = "Python bindings for libMcPhase";
    wrap_kernel(m);
}

