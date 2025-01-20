#include <pybind11/pybind11.h>

namespace py = pybind11;

void wrap_kernel(py::module &);

PYBIND11_MODULE(micromantid, m) {
    m.doc() = "Python bindings for microMantid";
    wrap_kernel(m);
}

