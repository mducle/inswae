const register_transmission = window.pyodide.runPython("import inswae; inswae.createSampleTransmission()");
window.osjs.make('osjs/packages').register("SampleTransmission", register_transmission);
