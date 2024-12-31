console.log("Initialising")

/* import * as Preact from 'https://esm.sh/preact'
import { signal } from 'https://esm.sh/@preact/signals'
import htm from 'https://esm.sh/htm'
const html = htm.bind(Preact.h)
import "https://cdn.plot.ly/plotly-2.27.0.min.js";
*/
import "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js";
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
  const exm = window.pyodide.runPython(`
    # Simple tutorial example
    from qtpy.QtWidgets import *
    app = QApplication([])
    window = QWidget()
    layout = QGridLayout()
    label = QLabel('0')
    def addone():
      label.setText(f'{int(label.text())+1}')
    plusbtn = QPushButton('+')
    plusbtn.clicked.connect(addone)
    minusbtn = QPushButton('-')
    minusbtn.clicked.connect(lambda: label.setText(f'{int(label.text())-1}'))
    editbox = QLineEdit('1')
    editbox.editingFinished.connect(lambda: label.setText(editbox.text()))
    frame = QFrame(window)
    frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
    frame.setLineWidth(2)
    frameLayout = QHBoxLayout()
    frameLayout.Direction = QBoxLayout.RightToLeft
    onBtn = QPushButton('On')
    offBtn = QPushButton('Off')
    stateLabel = QLabel('On')
    onBtn.clicked.connect(lambda: stateLabel.setText('On'))
    offBtn.clicked.connect(lambda: stateLabel.setText('Off'))
    frameLayout.addWidget(onBtn)
    frameLayout.addWidget(offBtn)
    frameLayout.addWidget(stateLabel)
    frame.setLayout(frameLayout)
    layout.addWidget(label, 0, 0)
    layout.addWidget(plusbtn, 1, 0)
    layout.addWidget(minusbtn, 0, 1)
    layout.addWidget(editbox, 2, 0, 1, 2)
    layout.addWidget(frame, 3, 0, 1, 3)
    window.setLayout(layout)
    window.show()
    app.exec()
  `);
  const pkg = core.make('osjs/packages');
  pkg.addPackages([ {
    "name": "Exm",
    "category": "utilities",
    "title": { "en_EN": "Exm" },
    "description": { "en_EN": "Example Python App" }
  } ]);
  pkg.register("Exm", exm);
  console.log(pkg.getPackages());
  pkg.launch('Exm');
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
  // Copies files in the overrides folder to Python site-packages folder
  fetch("./python-overrides.tgz").then( (response) => {
    response.arrayBuffer().then( (value) => {
      window.pyodide.unpackArchive(value, "gztar", {extractDir: "/lib/python3.11/site-packages/"});
    });
  });
  // Loads Python wheels
  for (const pkg of ["numpy"]) {//, "scipy", "matplotlib"]) {
    window.pyodide.loadPackage(pkg);
  }
};

// We need Pyodide to be loaded first before initialising OS.js as we
// need the Emscripten FS to be already initialised before osjs-VFS.
const pyodide = loadPyodide()
  .then((out) => {
    out.setDebug(true);
    document.getElementById("loading_spinner").remove();
    window.pyodide = out; 
    init_python();
    init_osjs();
  }
);
