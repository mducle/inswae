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
    # Test script of all currently implemented widgets
    from qtpy.QtWidgets import *
    msgbox = QMessageBox()
    msgbox.setText('An important message!')
    msgbox.exec()
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
    combo = QComboBox()
    combo.addItem('Apple')
    combo.addItems(['Pear', 'Orange'])
    combo.activated[str].connect(lambda text: stateLabel.setText(text))
    checkb = QCheckBox('Done?', window)
    checkb.stateChanged.connect(lambda state: stateLabel.setText(str(state)))
    checkb.setCheckState(True)
    tabs = QTabWidget()
    tabs.addTab(QLabel('Page 1'), 'P1')
    tabs.addTab(QLabel('Page 2'), 'P2')
    tabs.currentChanged.connect(lambda: stateLabel.setText(str(tabs.currentIndex())))
    frameLayout.addWidget(onBtn)
    frameLayout.addWidget(offBtn)
    frameLayout.addWidget(stateLabel)
    frame.setLayout(frameLayout)
    layout.addWidget(label, 0, 0)
    layout.addWidget(plusbtn, 1, 0)
    layout.addWidget(minusbtn, 0, 1)
    layout.addWidget(editbox, 2, 0, 1, 2)
    layout.addWidget(frame, 3, 0, 1, 2)
    layout.addWidget(combo, 4, 0)
    layout.addWidget(checkb, 4, 1)
    layout.addWidget(tabs, 5, 0, 1, 2)
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
  for (const pkg of ["numpy", "matplotlib"]) {//, "scipy"]) {
    await window.pyodide.loadPackage(pkg);
  }
/*
  // Ensure we use the HTML5 backend
  window.pyodide.runPython(`
    import matplotlib
    matplotlib.use("module://matplotlib_pyodide.html5_canvas_backend")
  `);
  const qe_app = window.pyodide.runPython("import inswae; inswae.create_QE_app()");
  const pkg = window.osjs.make('osjs/packages');
  pkg.addPackages([ { "name": "QECoverage", "category": "mantid",
    "title": { "en_EN": "QECoverage" },
    "description": { "en_EN": "Calculates Q-E kinematic limits" } } ]);
  pkg.register("QECoverage", qe_app);
  window.pyodide.runPython(`
    from qtpy.QtWidgets import *
    from matplotlib.figure import Figure
    from mantidqt.MPLwidgets import FigureCanvas
    import time
    import js
    window = QWidget()
    layout = QGridLayout()
    fig = Figure()
    canvas = FigureCanvas(fig)
    axes = fig.add_subplot(111)
    axes.plot(range(1,10), range(2,11))
    axes.axhline(color="k")
    axes.set_xlabel(r"$|Q|$ ($\AA^{-1}$)")
    axes.set_ylabel("Energy Transfer (meV)")
    canvas.draw()
    layout.addWidget(canvas, 0, 0)
    window.setLayout(layout)
    window.show()
  `);
*/
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
