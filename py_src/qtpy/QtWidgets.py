import js
import osjsGui
from pyodide.ffi import to_js, create_proxy
from js import Object, window
from hyperapp import h, text, app
import jswidgets
from .QtCore import Qt

QAPP = None

def toObj(in_dict):
    return to_js(in_dict, dict_converter=Object.fromEntries)

class EventProxy():
    def __init__(self, parent, name, wrapper=None):
        self.parent = parent
        self.name = name
        self.wrapper = wrapper
    def connect(self, callback):
        # Creates a wrapped callback
        if self.wrapper is None:
            self.parent._actions[self.name] = callback
        else:
            self.parent._actions[self.name] = self.wrapper(callback)

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

def action_wrap(state, actions, call):
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
                rendered = [obj.h(state, actions) for obj in self._widgets if hasattr(obj, 'h') and obj.isVisible()]
                return h(osjsGui.Box, toObj({'orientation':'horizontal'}), to_js(rendered))
            else:
                objs_list = []
                for r in range(len(widgets)):
                    rendered = [obj.h(state, actions) for obj in widgets[r] if hasattr(obj, 'h') and obj.isVisible()]
                    objs_list.append(h(osjsGui.Box, toObj({'orientation':'vertical'}), to_js(rendered)))
                return h(osjsGui.Box, toObj({'orientation':'horizontal'}), objs_list)
        self._views.append(create_proxy(createView))
        return app(toObj({'stateid':0}), toObj({'change':create_proxy(state_change)}), self._views[-1], content)
    def __del__(self):
        for v in self._views:
            del v

class QGridLayout(QLayout):
    def __init__(self, parent=None):
        super(QGridLayout, self).__init__(parent)
    def addWidget(self, widget, row, column, rowSpan=None, columnSpan=None, alignment=Qt.AlignCenter):
        self._widgets.append([widget, row, column, rowSpan, columnSpan])
        widget.parent = self
    def __call__(self, content, win):
        def createGrid(state, actions):
            nr = max([w[1] for w in self._widgets]) + 1
            nc = max([w[2] for w in self._widgets]) + 1
            gridcss = toObj({'display':'grid', 'grid-gap':'5px', 
                             'grid-template-columns':f'repeat({nc}, 1fr)', 'grid-template-rows':f'repeat({nr}, 1fr'})
            objs_list = []
            for w in self._widgets:
                rowspec = f'{w[1]+1}' if w[3] is None else f'{w[1]+1} / span {w[3]}'
                colspec = f'{w[2]+1}' if w[4] is None else f'{w[2]+1} / span {w[4]}'
                objs_list.append(h('div', toObj({'style':toObj({'grid-column':colspec, 'grid-row':rowspec})}), w[0].h(state, actions)))
            return h('div', toObj({'style':gridcss}), objs_list)
        self._views.append(create_proxy(createGrid))
        return app(toObj({'stateid':0}), toObj({'change':create_proxy(state_change)}), self._views[-1], content)

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
        self._text = ''
        self._flags = None
        self._hidden = False
        self._layout = None
        self._props = {}
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
    def text(self):
        return self._text
    def setText(self, text):
        self._text = text
    def hide(self):
        self._hidden = True
    def isVisible(self):
        return not self._hidden
    @property
    def content(self):
        return []
    def h(self, state, actions):
        props = {k:getattr(self, v) for k, v in self._props.items()}
        for k, v in self._actions.items():
            props[k] = create_proxy(action_wrap(state, actions, v))
        js.console.log(toObj(props))
        return h(self._element, toObj(props), self.content)
 
class QFrame(QWidget):
    def __init__(self, parent=None, flags=None):
        raise NotImplementedError

class QPushButton(QWidget):
    def __init__(self, text, parent=None):
        super(QPushButton, self).__init__(parent)
        self._text = text
        self._element = osjsGui.Button
        self._clicked = EventProxy(self, 'onclick')
        self._props = {'label':'_text'}
    @property
    def clicked(self):
        return self._clicked

class QLabel(QWidget):
    def __init__(self, text, parent=None):
        super(QLabel, self).__init__(parent)
        self._text = text
        self._element = jswidgets.TextLabel
        self._props = {'text':'_text'}

class QLineEdit(QWidget):
    def __init__(self, text, parent=None):
        super(QLineEdit, self).__init__(parent)
        self._text = text
        self._element = osjsGui.TextField
        self._props = {'value':'_text'}
        self._editingFinished = EventProxy(self, 'onchange', self._editingFinishedWrapper)
    def _editingFinishedWrapper(self, fn):
        def efWrap(event, value):
            self._text = value
            fn()
        return efWrap
    def setValidator(self, validator):
        pass
    def setToolTip(self, toolText):
        pass
    @property
    def editingFinished(self):
        return self._editingFinished
