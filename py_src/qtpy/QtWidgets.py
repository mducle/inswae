"""
An emulation layer to translate qtpy calls/widgets to hyperapp and OS.js widgets.
Does not strictly follow the Qt specifications but is meant to work with "real life" code.
Not all Qt features are implemented.
"""

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
                def createApp(content, win):
                    renderfn = create_proxy(self.window._layout.render_function)
                    return app(toObj({'stateid':0}), toObj({'change':create_proxy(state_change)}), renderfn, content)
                proc.createWindow(toObj({'title': self.window._title, 'dimension':self.window._size()})).render(createApp)
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
        self._styles = {}
    def addWidget(self, widget):
        self._widgets.append(widget) 
        widget.parent = self

class QGridLayout(QLayout):
    def __init__(self, parent=None):
        super(QGridLayout, self).__init__(parent)
    def addWidget(self, widget, row, column, rowSpan=None, columnSpan=None, alignment=Qt.AlignCenter):
        self._widgets.append([widget, row, column, rowSpan, columnSpan])
        widget.parent = self
    @property
    def render_function(self):
        def createGrid(state, actions):
            nr = max([w[1] for w in self._widgets]) + 1
            nc = max([w[2] for w in self._widgets]) + 1
            gridcss = toObj({'display':'grid', 'grid-gap':'5px', 
                             'grid-template-columns':f'repeat({nc}, auto)', 'grid-template-rows':f'repeat({nr}, auto'})
            objs_list = []
            for w in [obj for obj in self._widgets if obj[0].isVisible()]:
                rowspec = f'{w[1]+1}' if w[3] is None else f'{w[1]+1} / span {w[3]}'
                colspec = f'{w[2]+1}' if w[4] is None else f'{w[2]+1} / span {w[4]}'
                objs_list.append(h('div', toObj({'style':toObj({'grid-column':colspec, 'grid-row':rowspec})}), w[0].h(state, actions)))
            return h('div', toObj({'style':gridcss, **self._styles}), objs_list)
        return createGrid

class QFormLayout(QLayout):
    def __init__(self, parent=None):
        raise NotImplementedError

class MetaQBox(type):
    LeftToRight = property(lambda self: 'row')
    RightToLeft = property(lambda self: 'row-reverse')
    TopToBottom = property(lambda self: 'column')
    BottomToTop = property(lambda self: 'column-reverse')
    
class QBoxLayout(QLayout, metaclass=MetaQBox):
    def __init__(self, parent=None):
        super(QBoxLayout, self).__init__(parent)
        self._direction = 1
    def addStretch(self, stretch):
        pass
    @property
    def Direction(self):
        return self._direction
    @Direction.setter
    def Direction(self, value):
        self._direction = value
    @property
    def render_function(self):
        def createView(state, actions):
            rendered = []
            for obj in [w for w in self._widgets if w.isVisible()]:
                rendered.append(h('div', toObj({'style':toObj({'flex':'1'})}), obj.h(state, actions)))
            return h('div', toObj({'style': toObj({'display':'flex', 'flex-direction':self.Direction, **self._styles})}), to_js(rendered))
        return createView
        
class QHBoxLayout(QBoxLayout):
    def __init__(self, parent=None):
        super(QHBoxLayout, self).__init__(parent)
        self.Direction = QBoxLayout.LeftToRight

class QVBoxLayout(QBoxLayout):
    def __init__(self, parent=None):
        super(QVBoxLayout, self).__init__(parent)
        self.Direction = QBoxLayout.TopToBottom

class MetaQFrame(type):
    Plain = property(lambda self: 1)
    Raised = property(lambda self: 2)
    Sunken = property(lambda self: 4)
    NoFrame = property(lambda self: 8)
    Box = property(lambda self: 16)
    Panel = property(lambda self: 16)
    StyledPanel = property(lambda self: 16)
    HLine = property(lambda self: 32)
    VLine = property(lambda self: 64)

class QWidget():
    def __init__(self, parent=None):
        self.parent = parent
        self._title = ''
        self._text = ''
        self._flags = None
        self._hidden = False
        self._layout = None
        self._props = {}
        self._style = {}
        self._framestyle = {}
        self._actions = {}
        self._toolTip = ''
    def setWindowFlags(self, flags):
        self._flags = flags
    def setWindowTitle(self, title):
        self._title = title
    def setLayout(self, layout):
        self._layout = layout
    def _size(self):
        return {'width': 500 if 'width' not in self._style else self._style['width'],
                'height': 300 if 'height' not in self._style else self._style['height']}
    def show(self):
        if self.parent == None:   # Is an independent window
            if self._layout is None:
                raise RuntimeError('Custom top level widget has no layout')
            self._layout._styles = {**self._style, **self._framestyle}
            if QAPP is None:
                window_data = toObj({'title': self._title, 'dimension':self._size()})
                def createApp(content, win):
                    renderfn = create_proxy(self._layout.render_function)
                    return app(toObj({'stateid':0}), toObj({'change':create_proxy(state_change)}), renderfn, content)
                window.osjs.make('osjs/window', window_data).render(createApp)
            else:
                QAPP.set_window(self)
        else:
            self._hidden = False
    def text(self):
        return self._text
    def setText(self, text):
        self._text = text
    def currentText(self):
        return self._text
    def hide(self):
        self._hidden = True
    def isVisible(self):
        return not self._hidden
    def setFrameStyle(self, style):
        if (style | QFrame.NoFrame) == style:
            self._framestyle = {}
        elif (style | QFrame.HLine) == style:
            self._framestyle = {'border-style':{33:'solid', 34:'outset', 36:'inset'}[style]+' none none none', 'border-color':'white'}
        elif (style | QFrame.VLine) == style:
            self._framestyle = {'border-style':'none '+{64:'solid', 66:'outset', 68:'inset'}[style]+' none none', 'border-color':'white'}
        else:
            self._framestyle = {'border-style':{17:'solid', 18:'outset', 20:'inset'}[style], 'border-color':'white'}
    def setLineWidth(self, linewidth):
        self._framestyle.update({'border-width':f'{linewidth}px'})
    def setToolTip(self, text):
        self._toolTip = text
    def setValidator(self, validator):
        pass
    def setMaximumWidth(self, maxwidth):
        pass
    def content(self, state, actions):
        return []
    def h(self, state, actions):
        style = {**self._style, **self._framestyle}
        if self._layout is None:
            props = {k:(getattr(self, v) if isinstance(v, str) and hasattr(self, v) else v) for k, v in self._props.items()}
            if style:
                props['style'] = toObj(style)
            for k, v in self._actions.items():
                props[k] = create_proxy(action_wrap(state, actions, v))
            return h(self._element, toObj(props), self.content(state, actions))
        else:
            if style:
                self._layout._styles = style
            return self._layout.render_function(state, actions)
 
class QFrame(QWidget, metaclass=MetaQFrame):
    def __init__(self, parent=None, flags=None):
        super(QFrame, self).__init__(parent)
        self._element = 'div'

class QPushButton(QWidget):
    def __init__(self, text, parent=None):
        super(QPushButton, self).__init__(parent)
        self._text = text
        self._element = osjsGui.Button
        self._clicked = EventProxy(self, 'onclick', self._clickedWrapper)
        self._props = {'label':'_text'}
    def _clickedWrapper(self, fn):
        def clickWrap(event):
            fn()
        return clickWrap
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
        self._actions['onchange'] = self._editingFinishedWrapper(lambda:[])
        self._editingFinished = EventProxy(self, 'onchange', self._editingFinishedWrapper)
    def _editingFinishedWrapper(self, fn):
        def efWrap(event, value):
            self._text = value
            fn()
        return efWrap
    @property
    def editingFinished(self):
        return self._editingFinished

class QComboBoxActivatedProxy():
    # To handle both the .activated.connect and .activated[str].connect syntax
    def __init__(self, parent):
        self.parent = parent
    def connect(self, fn):
        def actWrap(event, value, choices):
            index = self.parent._items.index(value)
            self.parent._text = self.parent._items[index]
            fn(index)
        self.parent._actions['onchange'] = actWrap
    def __getitem__(self, inputtype):
        if isinstance(inputtype, str) or (inputtype == str):
            return self.parent._activated
        return self
            
class QComboBox(QWidget):
    def __init__(self, parent=None):
        super(QComboBox, self).__init__(parent)
        self._element = osjsGui.SelectField
        self._items = []
        self._text = ''
        self._activatedproxy = QComboBoxActivatedProxy(self)
        self._activated = EventProxy(self, 'onchange', self._activatedWrapper)
        self._props = {'choices':'_items'}
    def addItem(self, text):
        self._items.append(text)
        if self._text == '' and len(self._items) == 1:
            self._text = self._items[0]
    def addItems(self, texts):
        self._items += texts
        if self._text == '' and len(self._items) > 0:
            self._text = self._items[0]
    def clear(self):
        self._items = []
    def count(self):
        return len(self._items)
    def _activatedWrapper(self, fn):
        def actWrap(event, value, choices):
            self._text = value
            fn(value)
        return actWrap
    @property
    def activated(self):
        return self._activatedproxy

class QTabWidget(QWidget):
    def __init__(self, parent=None):
        super(QTabWidget, self).__init__(parent)
        self._element = osjsGui.Tabs
        self._tabs = []
        self._tabTitles = []
        self._props = {'labels':'_tabTitles', 'grow':1, 'shrink':1}
        self._currentChanged = EventProxy(self, 'onchange', self._currentChangedWrapper)
        self._index = 0
    def addTab(self, widget, title):
        self._tabs.append(widget)
        self._tabTitles.append(title)
    def currentIndex(self):
        return self._index
    def _currentChangedWrapper(self, fn):
        def changeWrap(event, index, value):
            self._index = index
            self._text = value
            fn()
        return changeWrap
    @property
    def currentChanged(self):
        return self._currentChanged
    def content(self, state, actions):
        return [w.h(state, actions) for w in self._tabs if w.isVisible()]

#class QStackedWidget(QWidget):
#    def __init__(self, parent=None):
#        super(QStackedWidget, self).__init__(parent)

class QMessageBox(QWidget):
    def __init__(self, parent=None):
        super(QMessageBox, self).__init__(parent)
    def show(self):
        self.exec()
    def exec(self):
        window.osjs.make('osjs/dialog', 'alert', toObj({'message':self._text, 'title':' ', 'sound':''}), create_proxy(lambda e, v, l:[]))

class QCheckBox(QWidget):
    def __init__(self, label, parent=None):
        super(QCheckBox, self).__init__(parent)
        self._element = osjsGui.ToggleField
        self._text = label
        self._checked = False
        self._props = {'label':'_text', 'checked':'_checked'}
        self._stateChanged = EventProxy(self, 'onchange', self._stateChangedWrapper)
    def setCheckState(self, state):
        self._checked = state
    def isChecked(self):
        return self._checked
    def _stateChangedWrapper(self, fn):
        def stateWrap(event, value):
            self._checked = value
            fn(value)
        return stateWrap
    @property
    def stateChanged(self):
        return self._stateChanged

"""
class QAction(QWidget):

class QDialog(QWidget):
class QFileDialog(QWidget):
class QMenu(QWidget):
class QMainWindow(QWidget):
class QSpacerItem(QWidget):
class QTextEdit(QWidget):
class QTableView(QWidget):
class QHeaderView(QWidget):
class QGroupBox(QWidget):
class QProgressDialog(QWidget):

"""
