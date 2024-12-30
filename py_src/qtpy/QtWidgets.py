import js
import osjsGui
from pyodide.ffi import to_js, create_proxy
from js import Object, window
from hyperapp import h, text, app
import inspect

QAPP = None
CALLBACK_TEST = False

def toObj(in_dict):
    return to_js(in_dict, dict_converter=Object.fromEntries)

class EventProxy():
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
    def connect(self, callback):
        self.parent._actions[self.name] = callback

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
                proc.createWindow(toObj({'title': self.window._title, 'dimension':{'width':500, 'height':300}})).render(self.window._layout)
            return callback
        """
        def createView(state, actions):
            def increment(event):
                print('inIncrement')
                js.console.log(event)
                actions.increment()
            return h('div', Object(), toObj([h('div', Object(), str(state.counter)), h('button', toObj({'type':'button', 'onclick': create_proxy(increment)}), 'Increment')]))
        def incstate(event):
            print('inIncstate')
            js.console.log(event)
            def inner(state, actions):
                print('inInner')
                js.console.log(actions)
                js.console.log(state)
                return toObj({'counter':state.counter+1})
            return create_proxy(inner)
        def createApp(content, win):
            print('inCreateApp')
            return app(toObj({'counter':0}), toObj({'increment':create_proxy(incstate)}), create_proxy(createView), content)
        def callback(core, args, options, metadata):
            print('inCallback')
            proc = window.osjs.make('osjs/application', toObj({'args':args, 'options':options, 'metadata':metadata}))
            proc.createWindow(toObj({'title': 'Example', 'dimension':{'width':500, 'height':300}})).render(createApp)
        return create_proxy(callback)
        """


def awrap(state, actions, call):
    def wrapper(*args, **kwargs):
        actions.change(state)
        call(*args, **kwargs)
    return wrapper

def state_change(event):
    def inner_state(state, actions):
        return toObj({'stateid':state.stateid+1})
    return create_proxy(inner_state)

class QLayout():
    def __init__(self, parent=None):
        self.parent = parent
        self._widgets = []
        self._views = []
    def addWidget(self, widget):
        self._widgets.append(widget) 
        widget.parent = self
    def __call__(self, content, win):
        def createView(state, actions):
            widgets = self.widgets
            if not isinstance(widgets[0], list) or len(widgets[0]) == 1:
                return h(osjsGui.Box, toObj({'orientation':'horizontal'}), to_js([obj.h(state, actions) for obj in self._widgets if hasattr(obj, 'h')]))
            else:
                objs_list = []
                for r in range(len(widgets)):
                    objs_list.append(h(osjsGui.Box, toObj({'orientation':'vertical'}), to_js([obj.h(state, actions) for obj in widgets[r] if hasattr(obj, 'h')])))
                return h(osjsGui.Box, toObj({'orientation':'horizontal'}), objs_list)
        self._views.append(create_proxy(createView))
        return app(toObj({'stateid':0}), toObj({'change':create_proxy(state_change)}), self._views[-1], content)
    def __del__(self):
        for v in self._views:
            del v

class QGridLayout(QLayout):
    def __init__(self, parent=None):
        super(QGridLayout, self).__init__(parent)
        self._widgets = [[ [] ]]
    def addWidget(self, widget, row, column, rowSpan=None, columnSpan=None, alignment=0):
        if row >= len(self._widgets):
            self._widgets += [[[]]*len(self._widgets[0]) for i in range(row + 1 - len(self._widgets))]
        if column >= len(self._widgets[0]):
            ndif = column + 1 - len(self._widgets[0])
            for r in range(len(self._widgets)):
                self._widgets[r] += [[]]*ndif
        self._widgets[row][column] = widget
        widget.parent = self
    @property
    def widgets(self):
        return self._widgets

class QFormLayout(QLayout):
    def __init__(self, parent=None):
        raise NotImplementedError

class MetaQBox(type):
    @property
    def LeftToRight(self):
        return 1
    @property
    def RightToLeft(self):
        return 2
    @property
    def TopToBottom(self):
        return 3
    @property
    def BottomToTop(self):
        return 4
    
class QBoxLayout(QLayout, metaclass=MetaQBox):
    def __init__(self, parent=None):
        super(QBoxLayout, self).__init__(parent)
        self._direction = 1
    @property
    def Direction(self):
        return self._direction
    @Direction.setter
    def Direction(self, value):
        self._direction = value
    @property
    def widgets(self):
        if self.Direction == QBoxLayout.TopToBottom:
            return self._widgets
        elif self.Direction == QBoxLayout.BottomToTop:
            return list(reversed(self._widgets))
        elif self.Direction == QBoxLayout.LeftToRight:
            return [self._widgets]
        elif self.Direction == QBoxLayout.RightToLeft:
            return [list(reversed(self._widgets))]
        
class QHBoxLayout(QBoxLayout):
    def __init__(self, parent=None):
        super(QHBoxLayout, self).__init__(parent)
        self.Direction = QBoxLayout.LeftToRight

class QVBoxLayout(QBoxLayout):
    def __init__(self, parent=None):
        super(QVBoxLayout, self).__init__(parent)
        self.Direction = QBoxLayout.TopToBottom

class QWidget():
    def __init__(self, parent=None):
        self.parent = parent
        self._title = ''
        self._flags = None
        self._hidden = False
        self._layout = None
        self._actions = {}
    def setWindowFlags(self, flags):
        self._flags = flags
    def setWindowTitle(self, title):
        self._title = title
    def setLayout(self, layout):
        self._layout = layout
    def show(self):
        if self.parent == None:   # Is an independent window
            if self._layout is None:
                raise RuntimeError('Custom top level widget has no layout')
            if QAPP is None:
                window_data = toObj({'title': self._title})
                window.osjs.make('osjs/window', window_data).render(self._layout)
            else:
                QAPP.set_window(self)
        else:
            self._hidden = False
            #self.parent.show()
    def hide(self):
        self._hidden = True
    def isVisible(self):
        return not self._hidden
 
class QFrame(QWidget):
    def __init__(self, parent=None, flags=None):
        raise NotImplementedError

class QPushButton(QWidget):
    def __init__(self, text, parent=None):
        super(QPushButton, self).__init__(parent)
        self.text = text
        self._clicked = EventProxy(self, 'clicked')
    @property
    def clicked(self):
        return self._clicked
    def h(self, state, actions):
        props = {'label': self.text}
        if 'clicked' in self._actions:
            props['onclick'] = create_proxy(awrap(state, actions, self._actions['clicked']))
        return h(osjsGui.Button, toObj(props))

class QLabel(QWidget):
    def __init__(self, text, parent=None):
        super(QLabel, self).__init__(parent)
        self.text = text
    def setText(self, text):
        self.text = text
    def h(self, state, actions):
        return h('div', Object(), self.text)

class QLineEdit(QWidget):
    def __init__(self, text, parent):
        super(QLineEdit, self).__init__(parent)
        self.text = text
        self._editingFinished = EventProxy(self, 'editingFinished')
    def setValidator(self, validator):
        pass
    def setToolTip(self, toolText):
        pass
    def setText(self, text):
        self.text = text
    def text(self):
        return self.text
    @property
    def editingFinished(self):
        return self._editingFinished
