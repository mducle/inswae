var targz = require('targz');

module.exports = {
  files: [
    "*.htm*", "*.css", "*.js",
    {
      match: ["py_src/**/*.py"],
      fn: (event, file) => {
        targz.compress({src:"py_src", dest:"python-overrides.tgz"});
      }
    }
  ]
}
