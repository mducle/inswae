const register_pychop = window.pyodide.runPython("import inswae; inswae.create_pychop()");
window.osjs.make('osjs/packages').register("PyChop", register_pychop);
