from js import ImageData, document
from matplotlib import interactive
from matplotlib.backend_bases import FigureManagerBase, NavigationToolbar2, _Backend
from matplotlib.backends import backend_agg
import mpljs
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import set_timeout

interactive(True)

class FigureCanvasJsAgg(backend_agg.FigureCanvasAgg):
    supports_blit = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._idle_scheduled = False
        self._id = "matplotlib_" + hex(id(self))[2:]
        self._title = ""
        self._jsfigure = None

    def show(self, *args, **kwargs):
        width, height = self.get_width_height()
        if self._jsfigure is None:
            self._jsfigure = mpljs.Figure.new(self._id, self._create_root_element(), width, height, self._title)
            if self.toolbar is not None:
                self._jsfigure.insertBefore(self.toolbar.get_element(), self._figure.message)
        self.draw()
 
    def draw(self):
        if self._jsfigure is None:
            return
        # Render the figure using Agg
        self._idle_scheduled = True
        orig_dpi = self.figure.dpi
        if self._jsfigure.ratio != 1:
            self.figure.dpi *= self._jsfigure.ratio
        pixels_proxy = None
        pixels_buf = None
        try:
            super().draw()
            # Copy the image buffer to the canvas
            width, height = self.get_width_height()
            canvas = self._jsfigure.canvas
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

    def _create_root_element(self):
        div = document.createElement("div")
        mpl_target = getattr(document, "pyodideMplTarget", document.body)
        mpl_target.appendChild(div)
        return div


@_Backend.export
class _BackendJsAgg(_Backend):
    FigureCanvas = FigureCanvasJsAgg
