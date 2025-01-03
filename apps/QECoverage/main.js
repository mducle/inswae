const register = window.pyodide.runPython("import inswae; inswae.create_QE_app()");
const pkg = window.osjs.make('osjs/packages')
pkg.register("QECoverage", register);
