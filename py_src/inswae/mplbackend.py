from io import BytesIO
from js import ImageData, document, alert
from matplotlib import interactive
from matplotlib.backend_bases import FigureManagerBase, NavigationToolbar2, _Backend, KeyEvent, LocationEvent, MouseEvent, ResizeEvent
from matplotlib.backends import backend_agg
import mpljs
import base64
import mimetypes
from pyodide.ffi import create_proxy, to_js
from pyodide.ffi.wrappers import set_timeout
from pathlib import Path

interactive(True)

_SPECIAL_KEYS_LUT = {'Alt': 'alt', 'AltGraph': 'alt', 'CapsLock': 'caps_lock', 'NumLock': 'num_lock', 'ScrollLock': 'scroll_lock',
                     'ArrowDown': 'down', 'ArrowLeft': 'left', 'ArrowRight': 'right', 'ArrowUp': 'up'}
_SPECIAL_KEYS = ['Control', 'Meta', 'Shift', 'Super', 'Enter', 'Tab', 'End', 'Home', 'PageDown', 'PageUp', 'Backspace', 'Delete', 'Insert',
                 'Escape', 'Pause', 'Select', 'Dead', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
def _handle_key(key):
    value = key[key.index('k') + 1:]
    if 'shift+' in key and len(value) == 1:
        key = key.replace('shift+', '')
    value = _SPECIAL_KEYS_LUT.get(value, value.lower() if value in _SPECIAL_KEYS else value) 
    return key[:key.index('k')] + value 

class FigureCanvasJsAgg(backend_agg.FigureCanvasAgg):
    supports_blit = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._idle_scheduled = False
        self._id = "matplotlib_" + hex(id(self))[2:]
        self._title = ""
        self.jsfig = None
        self._last_mouse_xy = (None, None)
        self.toolbar = NavigationToolbar2JsAgg(self)

    def show(self, *args, **kwargs):
        width, height = self.get_width_height()
        if self.jsfig is None:
            self.jsfig = mpljs.Figure.new(create_proxy(self), self._create_root_element(), width, height)
        self.draw()
 
    def draw(self):
        if self.jsfig is None:
            return
        # Render the figure using Agg
        self._idle_scheduled = True
        orig_dpi = self.figure.dpi
        if self.jsfig.ratio != 1:
            self.figure.dpi *= self.jsfig.ratio
        pixels_proxy = None
        pixels_buf = None
        try:
            super().draw()
            # Copy the image buffer to the canvas
            width, height = self.get_width_height()
            canvas = self.jsfig.canvas
            if canvas is None:
                return
            pixels = self.buffer_rgba().tobytes()
            pixels_proxy = create_proxy(pixels)
            pixels_buf = pixels_proxy.getBuffer("u8clamped")
            image_data = ImageData.new(pixels_buf.data, width, height)
            canvas.getContext("2d").putImageData(image_data, 0, 0)
        finally:
            self.figure.dpi = orig_dpi
            self._idle_scheduled = False
            if pixels_proxy:
                pixels_proxy.destroy()
            if pixels_buf:
                pixels_buf.release()

    def draw_idle(self):
        if not self._idle_scheduled:
            self._idle_scheduled = True
            set_timeout(self.draw, 1)

    def handle_mouse(self, e_type, x, y, button, step, modifiers, guiEvent):
        y = self.get_renderer().height - y
        self._last_mouse_xy = x, y
        # JavaScript button numbers and Matplotlib button numbers are off by 1.
        button = button + 1
        if e_type in ['button_press', 'button_release']:
            MouseEvent(e_type + '_event', self, x, y, button, modifiers=modifiers, guiEvent=guiEvent)._process()
        elif e_type == 'dblclick':
            MouseEvent('button_press_event', self, x, y, button, dblclick=True, modifiers=modifiers, guiEvent=guiEvent)._process()
        elif e_type == 'scroll':
            MouseEvent('scroll_event', self, x, y, step=step, modifiers=modifiers, guiEvent=guiEvent)._process()
        elif e_type == 'motion_notify':
            MouseEvent(e_type + '_event', self, x, y, modifiers=modifiers, guiEvent=guiEvent)._process()
        elif e_type in ['figure_enter', 'figure_leave']: LocationEvent(e_type + '_event', self, x, y, modifiers=modifiers, guiEvent=guiEvent)._process()

    def handle_key(self, e_type, key, guiEvent):
        KeyEvent(e_type + '_event', self, _handle_key(key), *self._last_mouse_xy, guiEvent=guiEvent)._process()

    def handle_toolbar_button(self, event):
        getattr(self.toolbar, event)()

    def handle_save(self, filetype):
        mimetype = mimetypes.types_map.get(f".{filetype}")
        if mimetype is None:
            alert(f"Cannot download plot, unable to determine mimetype for '{filetype}'")
            return
        element = document.createElement('a')
        data = BytesIO()
        self.figure.savefig(data, format=filetype)
        element.setAttribute("href", "data:{};base64,{}".format(mimetype, base64.b64encode(data.getvalue()).decode("ascii")))
        element.setAttribute("download", f"plot{self._id}.{format}")
        element.style.display = "none"
        document.body.appendChild(element)
        element.click()
        document.body.removeChild(element)

    def get_toolbar_items(self):
        return to_js([['']*4 if v[0] is None else list(v) for v in self.toolbar.toolitems])

    def get_toolbar_image(self, image):
        filename = Path(backend_agg.__file__).parent.parent / f"mpl-data/images/{image}.png"
        return to_js(filename.read_bytes())

    def _create_root_element(self):
        div = document.createElement("div")
        mpl_target = getattr(document, "pyodideMplTarget", document.body)
        mpl_target.appendChild(div)
        return div

_ALLOWED_TOOL_ITEMS = {'home', 'back', 'forward', 'pan', 'zoom', 'download', None}

class NavigationToolbar2JsAgg(NavigationToolbar2):
    toolitems = [v for v in (*NavigationToolbar2.toolitems, ('Download', 'Download plot', 'filesave', 'download'))
        if v[3] in _ALLOWED_TOOL_ITEMS]

    def __init__(self, canvas):
        self.message = ''
        super().__init__(canvas)

    def set_message(self, message):
        if message != self.message:
            self.canvas.jsfig.handle_message(message)
        self.message = message

    def draw_rubberband(self, event, x0, y0, x1, y1):
        self.canvas.jsfig.handle_rubberband(x0, x1, y0, y1)

    def remove_rubberband(self):
        self.canvas.jsfig.handle_rubberband(-1, -1, -1, -1)

    def save_figure(self, *args):
        """Save the current figure"""
        self.canvas.handle_save('png')

    def pan(self):
        super().pan()
        self.canvas.jsfig.handle_navigate_mode(self.mode.name)

    def zoom(self):
        super().zoom()
        self.canvas.jsfig.handle_navigate_mode(self.mode.name)

    def set_history_buttons(self):
        can_backward = self._nav_stack._pos > 0
        can_forward = self._nav_stack._pos < len(self._nav_stack) - 1
        if self.canvas.jsfig is not None:
            self.canvas.jsfig.handle_history_buttons(can_backward, can_forward);

@_Backend.export
class _BackendJsAgg(_Backend):
    FigureCanvas = FigureCanvasJsAgg
