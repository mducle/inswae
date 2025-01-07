const register_dgsplanner = window.pyodide.runPython("import inswae; inswae.create_dgsplanner()");
window.osjs.make('osjs/packages').register("DGSPlanner", register_dgsplanner);
