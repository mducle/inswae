import js
from qtpy.QtWidgets import QWidget
from matplotlib.backends.wasm_backend import FigureCanvasAggWasm, NavigationToolbar2AggWasm

class FigureCanvas(FigureCanvasAggWasm, QWidget):
    def __init__(self, *arg, **kwargs):
        FigureCanvasAggWasm.__init__(self, *arg, **kwargs)
        QWidget.__init__(self)
        self._element = 'iframe'
        self._style = {'border':'none'}
        self._actions = {'onload':self._onloadWrapper()}
        self.toolbar = NavigationToolbar2AggWasm(self)
        self._init = False
        self._div = js.document.getElementById(self._id + '_rootdiv')
        if not self._div:
            self._div = js.document.createElement('div')
            self._div.id = self._id + '_rootdiv'
    def _onloadWrapper(self):
        def loadWrap(event):
            if not self._init or not js.document.getElementById(self._id + '_rootdiv'):
                self._init = True
                event.target.parentNode.append(self._div)
                event.target.remove()
                self.show()
        return loadWrap
    def show(self):
        # Both FigureCanvasAggWasm and QWidget have show()
        FigureCanvasAggWasm.show(self) 
    def updateGeometry(self):
        pass
    def _create_root_element(self):
        # Overrides so it is not included in the "pyodideMplTarget" element
        return self._div

FigureCanvasQTAgg = FigureCanvas

# Never render navigation toolbar separately, always bundle it a FigureCanvas
class NavigationToolbar2QT():
    def __init__(self, canvas, parent, coordinates=True):
        pass
    def isVisible(self):
        return False
    def hide(self): ...
