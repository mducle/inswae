const admzip = require("adm-zip");

// Wait until files are full created
setTimeout(() => {}, 1000);

const zip = new admzip();
zip.addLocalFolder("py_src", ".");
zip.writeZip("python-overrides-1.0.0-py2.py3-none-any.whl");

const zip2 = new admzip();
zip2.addLocalFolder("mslice/src", ".");
zip2.writeZip("mslice-1.0.0-py2.py3-none-any.whl");
