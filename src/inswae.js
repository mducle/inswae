console.log("Initialising")

/* import * as Preact from 'https://esm.sh/preact'
import { signal } from 'https://esm.sh/@preact/signals'
import htm from 'https://esm.sh/htm'
const html = htm.bind(Preact.h)
import "https://cdn.plot.ly/plotly-2.27.0.min.js";
*/
import "https://cdn.jsdelivr.net/pyodide/v0.27.1/full/pyodide.js";
import "https://cdn.jsdelivr.net/npm/@osjs/gui/dist/main.js";
import "https://cdn.jsdelivr.net/npm/@osjs/client/dist/main.js";
import "https://cdn.jsdelivr.net/npm/@osjs/panels/dist/main.js";
import "https://cdn.jsdelivr.net/npm/@osjs/dialogs/dist/main.js";
import EmscriptenFSAdapter from "./emfs-adapter.js";
import { jswidgets } from "./widgets.js";

console.log("Imported JS from CDNs")

const {
  Core,
  CoreServiceProvider,
  DesktopServiceProvider,
  VFSServiceProvider,
  NotificationServiceProvider,
  SettingsServiceProvider,
  AuthServiceProvider } = osjsClient;
const { GUIServiceProvider } = osjsGui;
const { PanelServiceProvider } = osjsPanels;
const { DialogServiceProvider } = osjsDialogs;
const { h, text, app } = hyperapp;

const config = {
  standalone: true,
  auth: {
    login: {
      username: "demo",
      password: "demo" 
    }
  },
  desktop: {
    settings: {
      font: "sans-serif",
      sounds: false
    }
  },
  vfs: {
    defaultAdapter: "emscripten",
    mountpoints: [
      {name: "apps", label: "Applications", adapter: "apps", attributes: { visibility: "restricted", readOnly: true } },
      {name: "osjs", label: "OS.js", adapter: "emscripten", icon: {name: "folder-publicshare"} },
      {name: "home", label: "Home", adapter: "emscripten", icon: {name: "user-home"} }
    ]
  }
};

const onStarted = core => {
};

const init_osjs = () => {
  const osjs = new Core(config, {
    omit: ["vfs.mountpoints"]
  });

  // Register your service providers
  osjs.register(CoreServiceProvider);
  osjs.register(DesktopServiceProvider);
  osjs.register(VFSServiceProvider, {
    args: { 
      adapters: { emscripten: EmscriptenFSAdapter },
    }
  });
  osjs.register(NotificationServiceProvider);
  osjs.register(SettingsServiceProvider, { before: true });
  osjs.register(AuthServiceProvider, { before: true });
  osjs.register(PanelServiceProvider);
  osjs.register(DialogServiceProvider);
  osjs.register(GUIServiceProvider);

  // Your own shenanigans
  osjs.once("osjs/core:started", () => onStarted(osjs));

  window.osjs = osjs;
  osjs.boot();
};

//window.addEventListener('DOMContentLoaded', () => init_osjs());
async function init_python() {
  // Registers OS.js modules to be able to access them from Python
  window.pyodide.registerJsModule("osjsGui", osjsGui);
  window.pyodide.registerJsModule("osjsPanels", osjsPanels);
  window.pyodide.registerJsModule("osjsDialogs", osjsDialogs);
  window.pyodide.registerJsModule("hyperapp", {h:h, text:text, app:app});
  window.pyodide.registerJsModule("jswidgets", jswidgets);
  const fs = window.pyodide.FS;
  // Loads Python wheels
  for (const pkg of ["numpy", "pyyaml", "matplotlib"]) {//, "scipy"]) {
    await window.pyodide.loadPackage(pkg);
  }
  // Installs mantid
  await window.pyodide.loadPackage("micromantid-0.0.1-cp312-cp312-pyodide_2024_0_wasm32.whl");
  // Copies files in the overrides folder to Python site-packages folder
  await window.pyodide.loadPackage("python-overrides-1.0.0-py2.py3-none-any.whl");
  await window.pyodide.loadPackage("mslice-1.0.0-py2.py3-none-any.whl");
  // Imports matplotlib and Mantid now to save time on initialising apps
  await window.pyodide.runPython(`
      import matplotlib.pyplot
      import mantid.simpleapi
  `);
  document.getElementById("loading_spinner").remove();
  // Creates shortcuts
  if (!fs.analyzePath('/home/pyodide/.desktop').exists) { fs.mkdir('/home/pyodide/.desktop'); }
  const shortobj = '{"isDirectory": false, "isFile": true, "mime": "osjs/application", "size": 0, ' + 
                   '"label": null, "stat": {}, "id": null, "parent_id": null, "humanSize": "0 B", '
  fs.writeFile('/home/pyodide/.desktop/.shortcuts.json', '[' +
     shortobj + '"icon": "apps/QECoverage/qecoverage.png", "path": "apps:/QECoverage", "filename": "QECoverage" }, ' +
     shortobj + '"icon": "apps/TofConverter/tofconverter.png", "path": "apps:/TofConverter", "filename": "TofConverter" }, ' +
     shortobj + '"icon": "apps/SampleTransmission/icon.png", "path": "apps:/SampleTransmission", "filename": "SampleTransmission" }, ' +
     shortobj + '"icon": "apps/PyChop/icon.png", "path": "apps:/PyChop", "filename": "PyChop" }, ' +
     shortobj + '"icon": "apps/DGSPlanner/icon.png", "path": "apps:/DGSPlanner", "filename": "DGSPlanner" }, ' +
     shortobj + '"icon": "favicon.ico", "path": "apps:/MSlice", "filename": "MSlice" }'
  +']');
  window.osjs.make('osjs/settings').set('osjs/desktop', 'iconview.enabled', true).save()
/*
  const exm = window.pyodide.runPython(`
    # Test script of all currently implemented widgets
    from qtpy.QtWidgets import *
    app = QApplication([])
    window = QWidget()
    layout = QHBoxLayout()
    label = QLabel('Spin!')
    spinner = QDoubleSpinBox()
    layout.addWidget(label)
    layout.addWidget(spinner)
    window.setLayout(layout)
    window.show()
    app.exec()
  `);
  const pkg = window.osjs.make('osjs/packages');
  pkg.addPackages([ {
    "name": "Exm",
    "category": "utilities",
    "title": { "en_EN": "Exm" },
    "description": { "en_EN": "Example Python App" }
  } ]);
  pkg.register("Exm", exm);
  console.log(pkg.getPackages());
  pkg.launch('Exm');

  window.pyodide.runPython(`
    from mantid.simpleapi import CalculateSampleTransmission
    transmission_ws = CalculateSampleTransmission(
        WavelengthRange='0.0,0.2,2.0',
        ChemicalFormula='Li',
        DensityType='Mass Density',
        density=0.1,
        thickness=0.1,
    )
  `);
*/
};

// We need Pyodide to be loaded first before initialising OS.js as we
// need the Emscripten FS to be already initialised before osjs-VFS.
const pyodide = loadPyodide()
  .then((out) => {
    out.setDebug(true);
    window.pyodide = out; 
    init_python();
    init_osjs();
  }
);
