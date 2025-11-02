const register_mslice = window.pyodide.runPython("import inswae; inswae.createMSlice()");
window.osjs.make('osjs/packages').register("MSlice", register_mslice);
