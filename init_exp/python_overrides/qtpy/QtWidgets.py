import js
from pyodide.ffi import to_js
from js import Object, window, osjsGui
from hyperapp import h, text, app

QAPP = None

class QApplication():
    def __init__(self, args):
        self.proc = window.osjs.make('osjs/application')
        global QAPP
        QAPP = self.proc
    def exec(self):
        global QAPP
        QAPP = None

class QLayout():
    def __init__(self, parent=None):
        self.parent = parent
        self._widgets = []
    def addWidget(self, widget):
        self._widgets.append(widget) 

class QGridLayout(QLayout):
    def __init__(self, parent=None):
        raise NotImplementedError

class QFormLayout(QLayout):
    def __init__(self, parent=None):
        raise NotImplementedError
    
class QBoxLayout(QLayout):
    _LeftToRight = 1
    _RightToLeft = 2
    _TopToBottom = 3
    _BottomToTop = 4
    def __init__(self, parent=None):
        super(QBoxLayout, self).__init__(parent)
        self._direction = self._LeftToRight
    @property
    def LeftToRight(self):
        return self._LeftToRight
    @property
    def RightToLeft(self):
        return self._RightToLeft
    @property
    def TopToBottom(self):
        return self._TopToBottom
    @property
    def BottomToTop(self):
        return self._BottomToTop
    @property
    def Direction(self):
        return self._direction
    @Direction.setter
    def Direction(self, value):
        self._direction = value
    def __call__(self, value, val):
        js.console.log(value)
        js.console.log(val)
        def createView(state, actions):
            vv = [obj.h() for obj in self._widgets]
            js.console.log(vv)
            return vv
        return app(Object(), Object(), createView, val)
        
class QHBoxLayout(QBoxLayout):
    def __init__(self, parent=None):
        super(QHBoxLayout, self).__init__(parent)
        self.Direction = QBoxLayout.LeftToRight

class QVBoxLayout(QBoxLayout):
    def __init__(self, parent=None):
        super(QVBoxLayout, self).__init__(parent)
        self.Direction = QBoxLayout.TopToBottom

class DummyProc():
    def createWindow(self, window_data):
        return osjs.make('osjs/window', window_data)

class QWidget():
    def __init__(self, parent=None):
        global QAPP
        self.parent = parent
        self._title = ''
        self._flags = None
        self.proc = QAPP if QAPP else DummyProc()
    def setWindowFlags(self, flags):
        self._flags = flags
    def setWindowTitle(self, title):
        self._title = title
    def setLayout(self, layout):
        self._layout = layout
    def show(self):
        if self.parent == None:   # Is an independent window
            window_data = to_js({'title': self._title}, dict_converter=Object.fromEntries)
            self.proc.createWindow(window_data).render(self._layout)
        else:
            self.parent.show()
 

class QFrame(QWidget):
    def __init__(self, parent=None, flags=None):
        pass

class QPushButton(QWidget):
    def __init__(self, text, parent=None):
        self.parent = parent
        self.text = text
    def h(self):
        return h(osjsGui.Button, to_js({'label': self.text}, dict_converter=Object.fromEntries))
