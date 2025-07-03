import js
import uuid
from pyodide.code import run_js
from qtpy.QtWidgets import QWidget
from matplotlib.backends.backend_webagg import FigureManagerWebAgg, WebAggApplication
from matplotlib.backends.backend_webagg_core import FigureCanvasWebAggCore, NavigationToolbar2WebAgg

FIGNUM = 0

class FigureCanvas(FigureCanvasWebAggCore, QWidget):
    def __init__(self, figure=None):
        super().__init__(figure=figure)
        self._element = 'iframe'
        self._style = {'border':'none'}
        self._id = f'mplfig{str(uuid.uuid4())[:6]}'
        WebAggApplication.initialize()
        self.js_fig = None
        self._num = 0
        self._init = False
        self._div = js.document.getElementById(self._id)
        if not self._div:
            self._div = js.document.createElement('div')
            self._div.id = self._id
            js.document.body.append(self._div)
            self._div.style.visibility = 'hidden'
        def loadWrap(event):
            if not self._init or not js.document.getElementById(self._id):
                self._init = True
                self._div.remove()
                self._div.style.visibility = 'visible'
                event.target.parentNode.append(self._div)
                event.target.remove()
                self.show()
        self._actions = {'onload': loadWrap}
    def _get_manager(self):
        if self.manager is None:
            global FIGNUM
            self.manager = FigureManagerWebAgg(self, FIGNUM)
            self._num = FIGNUM
            FIGNUM += 1
    def draw(self):
        self._get_manager()
        FigureCanvasWebAggCore.draw(self)
    def show(self):
        self._get_manager()
        fignum = self._num
        if self.js_fig is None:
            js_code = \
                """
                var websocket_type = mpl.get_websocket_type();
                var fig = new mpl.figure(fig_id, new websocket_type(fig_id), null, document.getElementById(parent_id));
                fig;
                """
            js_code = f"var fig_id = '{fignum}'; var parent_id = '{self._id}'; " + js_code
            self.js_fig = run_js(js_code)
            web_socket = WebAggApplication.MockPythonWebSocket(self.manager, self.js_fig.ws)
            web_socket.open(fignum)
    def updateGeometry(self):
        pass

FigureCanvasQTAgg = FigureCanvas

# Never render navigation toolbar separately, always bundle it a FigureCanvas
class NavigationToolbar2QT(NavigationToolbar2WebAgg, QWidget):
    def __init__(self, canvas, parent=None, coordinates=True):
        NavigationToolbar2WebAgg.__init__(self, canvas)
        QWidget.__init__(self, parent)
