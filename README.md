# Inelastic Neutron Scattering Web Analysis Environment

The Inelastic Neutron Scattering Web Analysis Environment (`inswae`) is a port of commonly used
utilies from the [mantid](https://mantidproject.org/) program to run directly in the browser
(without a server).

## For Developers

You should have `node.js` installed. Run:

```
npm install
npm run start
```

This will start a local simple webserver and watch for file changes, reloading the browser when
a source file changes.

We use [OS.js](https://www.os-js.org/) for the virtual desktop and [pyodide](https://pyodide.org)
to run the Python code.

The app is a single-page application and aside from zipping the Python source files there is no
compiling required.
