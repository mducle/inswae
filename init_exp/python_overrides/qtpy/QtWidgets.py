import js
import osjsGui
from pyodide.ffi import to_js, create_proxy
from js import Object, window
from hyperapp import h, text, app

QAPP = None

def toObj(in_dict):
    return to_js(in_dict, dict_converter=Object.fromEntries)

class QApplication():
    def __init__(self, args):
        self.window = None
        global QAPP
        QAPP = self
    def set_window(self, window):
        self.window = window
    def exec(self):
        global QAPP
        QAPP = None
        if self.window is not None:
            def callback(core, args, options, metadata):
                proc = window.osjs.make('osjs/application', toObj({'args':args, 'options':options, 'metadata':metadata}))
                proc.createWindow(toObj({'title': self.window._title})).render(self.window._layout)
            return callback

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
    def __call__(self, content, win):
        def createView(state, actions):
            return h('div', Object(), to_js([obj.h() for obj in self._widgets]))
        return app(Object(), Object(), create_proxy(createView), content)
        
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
        return window.osjs.make('osjs/window', window_data)

class QWidget():
    def __init__(self, parent=None):
        self.parent = parent
        self._title = ''
        self._flags = None
    def setWindowFlags(self, flags):
        self._flags = flags
    def setWindowTitle(self, title):
        self._title = title
    def setLayout(self, layout):
        self._layout = layout
    def show(self):
        if self.parent == None:   # Is an independent window
            if QAPP is None:
                window_data = toObj({'title': self._title})
                window.osjs.make('osjs/window', window_data).render(self._layout)
            else:
                QAPP.set_window(self)
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
        return h(osjsGui.Button, toObj({'label': self.text}))
