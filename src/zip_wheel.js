const admzip = require("adm-zip");

const zip = new admzip();
zip.addLocalFolder("py_src", ".");
zip.writeZip("python-overrides-1.0.0-py2.py3-none-any.whl");
