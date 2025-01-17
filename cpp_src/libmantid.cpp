
#include <pybind11/pybind11.h>

namespace py = pybind11;

void wrap_kernel(py::module &);

PYBIND11_MODULE(libmantid, m) {
    m.doc() = "Python bindings for libMantid";
    wrap_kernel(m);
}

