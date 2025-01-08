const admzip = require("adm-zip");
const { unlinkSync } = require('node:fs');

module.exports = {
  files: [
    "*.htm*", "*.css", "*.js",
    {
      match: ["py_src/**/*.py"],
      fn: (event, file) => {
        try {
          unlinkSync("python-overrides.whl");
        } catch (err) {
          console.log(err)
        }
        const zip = new admzip();
        zip.addLocalFolder("py_src", ".");
        zip.writeZip("python-overrides.whl");
      }
    }
  ]
}
