const register_tofconverter = window.pyodide.runPython("import inswae; inswae.createTofConverter()");
window.osjs.make('osjs/packages').register("TofConverter", register_tofconverter);
