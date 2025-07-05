const register_qecoverage = window.pyodide.runPython("import inswae; inswae.create_QE_app()");
window.osjs.make('osjs/packages').register("QECoverage", register_qecoverage);
