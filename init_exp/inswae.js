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
/*desktop: {
    iconview: {
      enabled: false },
    contextmenu: {
      enabled: false },
    settings: {
      font: "sans-serif",
      sounds: false,
      panels: [{
        position: "top",
        items: [
        { name: "windows" },
        { name: "tray" },
        { name: "clock" }] }] 
    } 
  }*/
};

const onStarted = core => {
  // Basic window example
  core.make("osjs/window", {
    title: "UMD Example",
    dimension: { width: 400, height: 200 },
    position: "center" }).
  render($content => {
    $content.appendChild(
    document.createTextNode(
    "Hello World!"));
  });
  /*
  core.make("osjs/packages").launch("Calculator").then(result => {
    console.log(result)
    if (result.errors.length) {
      logger.error(result.errors); }
    return result;});
  */
  const fs = core.make('osjs/fs');
  console.log(fs);
  console.log(fs.mountpoints());
  const vfs = core.make('osjs/vfs');
  console.log(vfs);
  vfs.readdir('osjs:/').then( (list) => {
    console.log(list);
  });
  //console.log(vfs.readfile('osjs:/lib/python3.11/site-packages/numpy-1.25.2.dist-info/top_level.txt', 'string'));
  //console.log(vfs.writefile('osjs:/home/test.txt', 'this is a text'));
  //console.log(vfs.url('osjs:/home/test.txt'));
  console.log(core.configuration);
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

async function init_pyodide() {
  // Loads Pyodide async whilst setting up OS.JS
  for (const pkg of ["numpy", "pyyaml"]) {
    await window.pyodide.loadPackage(pkg);
  }
  console.log("Imported Numpy and PyYaml")
};

//window.addEventListener("DOMContentLoaded", () => init_osjs());
const pyodide = loadPyodide()
  .then((out) => {
    const load_spinner = document.getElementById("loading_spinner");
    load_spinner.remove();
    window.pyodide = out; 
    init_pyodide();
    init_osjs();
  }
);
