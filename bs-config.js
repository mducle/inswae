const targz = require('targz');
const { unlinkSync } = require('node:fs');

module.exports = {
  files: [
    "*.htm*", "*.css", "*.js",
    {
      match: ["py_src/**/*.py"],
      fn: (event, file) => {
        try {
          unlinkSync("python-overrides.tgz");
        } catch (err) {
          console.log(err)
        }
        targz.compress({src:"py_src", dest:"python-overrides.tgz"});
        setTimeout(() => {}, 1000); // Sleep 1s
      }
    }
  ]
}
