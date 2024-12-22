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
      username: 'demo',
      password: 'demo' } },


  desktop: {
    iconview: {
      enabled: false },

    contextmenu: {
      enabled: false },

    settings: {
      font: 'sans-serif',
      sounds: false,
      panels: [{
        position: 'top',
        items: [
        { name: 'windows' },
        { name: 'tray' },
        { name: 'clock' }] }] } } };






const onStarted = core => {
  // Basic window example
  core.make('osjs/window', {
    title: 'UMD Example',
    dimension: { width: 400, height: 200 },
    position: 'center' }).
  render($content => {
    $content.appendChild(
    document.createTextNode(
    'Hello World!'));


  });
};

const init = () => {
  const osjs = new Core(config, {});

  // Register your service providers
  osjs.register(CoreServiceProvider);
  osjs.register(DesktopServiceProvider);
  osjs.register(VFSServiceProvider);
  osjs.register(PanelServiceProvider);
  osjs.register(NotificationServiceProvider);
  osjs.register(SettingsServiceProvider, { before: true });
  osjs.register(AuthServiceProvider, { before: true });
  osjs.register(DialogServiceProvider);
  osjs.register(GUIServiceProvider);

  // Your own shenanigans
  osjs.once('osjs/core:started', () => onStarted(osjs));

  osjs.boot();
};

window.addEventListener('DOMContentLoaded', () => init());
//# sourceURL=pen.js
