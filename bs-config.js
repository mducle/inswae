const admzip = require("adm-zip");
const { unlinkSync } = require('node:fs');

module.exports = {
  files: [
    "*.htm*", "*.css", "*.js",
    {
      match: ["py_src/**/*.py"],
      fn: (event, file) => {
        try {
          unlinkSync("python-overrides-1.0.0-py2.py3-none-any.whl");
        } catch (err) {
          console.log(err)
        }
        const zip = new admzip();
        zip.addLocalFolder("py_src", ".");
        zip.writeZip("python-overrides-1.0.0-py2.py3-none-any.whl");
      }
    },
    {
      match: ["mslice/src/mslice/**/*.py"],
      fn: (event, file) => {
        try {
          unlinkSync("mslice-1.0.0-py2.py3-none-any.whl");
        } catch (err) {
          console.log(err)
        }
        const zip = new admzip();
        zip.addLocalFolder("mslice/src", ".");
        zip.writeZip("mslice-1.0.0-py2.py3-none-any.whl");
      }
    }
  ]
}
