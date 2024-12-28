console.log("Initialising")

import { h, text, app } from "https://unpkg.com/hyperapp"
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

console.log("Imported JS from CDNs")

const {
  Core,
  CoreServiceProvider,
  DesktopServiceProvider,
  VFSServiceProvider,
  NotificationServiceProvider,
  SettingsServiceProvider,
  AuthServiceProvider } =
osjsClient;

const { GUIServiceProvider } = osjsGui;
const { PanelServiceProvider } = osjsPanels;
const { DialogServiceProvider } = osjsDialogs;

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
/*
  window.pyodide.runPython(`
    #from pyodide.ffi import to_js
    #from js import window, Object
    #window_data = to_js({'title':'Example', 'dimension': {'width': 400, 'height':200}, 'position':'center'}, dict_converter=Object.fromEntries)
    #window.osjs.make("osjs/window", window_data).render()
    from qtpy.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QPushButton('Top'))
    layout.addWidget(QPushButton('Bottom'))
    window.setLayout(layout)
    window.show()
    app.exec()
  `);
*/
// /*
  const createView = (state, actions) => {
    console.log('inCreateView');
    console.log(state);
    return h('div', {}, [
    h('div', {}, String(state.counter)),
    h('button', {type: 'button', onclick: () => actions.increment()}, 'Increment counter')
  ]);
  };
  const createApp = (content) => {
    console.log('inCreateApp');
    console.log(content);
    //app({init:{counter:0}, view:createView, node:content});
    app({
      counter: 0
    }, {
      increment: () => state => ({counter: state.counter + 1})
    }, createView, content);
  };
  //const proc = core.make('osjs/application');
  //const win = proc.createWindow({title:'Exm', dimension:{width:300, heigh:300}}).render((content, win) => createApp(content));
  //const win = core.make('osjs/window', {title:'Exm', dimension:{width:300, heigh:300}}).render((content, win) => createApp(content));
  //core.make("osjs/window", { title: "UMD Example", dimension: { width: 200, height: 200 }, position: "center" }).render();
  const pkg = core.make('osjs/packages');
  pkg.addPackages([ {
    "name": "Exm",
    "category": "utilities",
    "title": { "en_EN": "Exm" },
    "description": { "en_EN": "File Manager" }
  } ]);
  pkg.register("Exm", (core, args, options, metadata) => {
    const proc = core.make('osjs/application', {args, options, metadata});
    proc.createWindow({title:'Exm', dimension:{width:300, heigh:300}}).render((content, win) => createApp(content));
    return proc;
  });
  console.log(pkg);
  console.log(pkg.getPackages());
  pkg.launch('Exm');
  pkg.launch('FileManager');
  
// */
  //console.log(core);
  //const pkg = core.make('osjs/packages');
  //console.log(pkg);
  //console.log(pkg.getPackages());
  //console.log(pkg.packages);
  //console.log(pkg.metadata);
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

async function init_python() {
  // Registers OS.js modules to be able to access them from Python
  window.pyodide.registerJsModule("osjsGui", osjsGui);
  window.pyodide.registerJsModule("osjsPanels", osjsPanels);
  window.pyodide.registerJsModule("osjsDialogs", osjsDialogs);
  window.pyodide.registerJsModule("hyperapp", {h:h, text:text, app:app});
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
    document.getElementById("loading_spinner").remove();
    window.pyodide = out; 
    init_python();
    init_osjs();
  }
);
