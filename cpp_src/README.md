# microMantid

microMantid is a fork of [Mantid 6.12](https://github.com/mantidproject/mantid/releases/tag/v6.12.0) 
containing only a subset of the core Framework without the Workbench or GUI interfaces, and refactored
to use [pybind11](https://github.com/pybind/pybind11) instead of [boost::python](https://github.com/boostorg/python)
targetted at the [WebAssembly](https://webassembly.org/) platform so that it can run client-side-only
within a web-browser.
