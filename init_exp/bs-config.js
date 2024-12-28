var targz = require('targz');

module.exports = {
  files: [
    "*.htm*", "*.css", "*.js",
    {
      match: ["python_overrides/**/*.py"],
      fn: (event, file) => {
        targz.compress({src:"python_overrides", dest:"python-overrides.tgz"});
      }
    }
  ]
}
