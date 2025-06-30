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
from . import QtCore
from .QtCore import Qt
from collections import OrderedDict
import os
import datetime

QAPP = None

def toObj(in_dict):
    return to_js(in_dict, dict_converter=Object.fromEntries)

class EventProxy():
    def __init__(self, parent, name, wrapper=None):
        self.parent = parent
        self.name = name
        self.wrapper = wrapper
    def connect(self, callback):
        def _send_wrapper(*args, **kwargs):
            if hasattr(callback, '__self__'):
                callback.__self__._sender = self.parent
            callback(*args, **kwargs)
        if self.wrapper is None:
            self.parent._actions[self.name] = _send_wrapper
        else:
            self.parent._actions[self.name] = self.wrapper(_send_wrapper)

class QApplication():
    def __init__(self, args):
        self.window = None
        global QAPP
        QAPP = self
        self._lastwindowclosed = QtCore.Signal()
        self._proc = None
    def set_window(self, window):
        self.window = window
    @staticmethod
    def instance():
        global QAPP
        return QAPP
    @staticmethod
    def processEvents(): ...
    @property
    def lastWindowClosed(self):
        return self._lastwindowclosed
    def quit(self): ...
    def exec(self):
        if self.window is not None:
            def callback(core, args, options, metadata):
                proc = window.osjs.make('osjs/application', toObj({'args':args, 'options':options, 'metadata':metadata}))
                def createApp(content, win):
                    renderfn = create_proxy(self.window._layout.render_function)
                    return app(toObj({'stateid':0}), toObj({'change':create_proxy(state_change)}), renderfn, content)
                self.window._jswindow = proc.createWindow(toObj({'title': self.window._title, 'dimension':self.window._size()})).render(createApp)
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
    def addWidget(self, widget, *args, **kwargs):
        self._widgets.append(widget) 
        widget.parent = self
    def addItem(self, item): ...
    def sizeHint(self): ...
    def replaceWidget(self, old, new):
        found = False
        for i, w in enumerate(self._widgets):
            if (w[0] if isinstance(w, list) else w) == old:
                found = True
                break
        if found:
            if isinstance(w, list):
                self._widgets[i][0] = new
            else:
                self._widgets[i] = new
            new.parent = self
    def insertWidget(self, index, widget, *args, **kwargs):
        self._widgets.insert(index, widget)
        widget.parent = self
    def addLayout(self, layout, *args):
        widget = QWidget()
        widget.setLayout(layout)
        self.addWidget(widget, *args)
    def setContentsMargins(self, left, top, right, bottom): ...
    def setSpacing(self, value): ...
    def __call__(self):
        return self

class QGridLayout(QLayout):
    def __init__(self, parent=None):
        super(QGridLayout, self).__init__(parent)
    def addWidget(self, widget, row=0, column=0, rowSpan=None, columnSpan=None, alignment=Qt.AlignCenter):
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
    def addStretch(self, stretch): ...
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

class QStackedLayout(QLayout):
    def __init__(self, parent=None):
        super(QStackedLayout, self).__init__(parent)
        self._currentIndex = 0
    def setCurrentIndex(self, index):
        self._currentIndex = index
    def setCurrentWidget(self, widget):
        raise NotImplementedError('setCurrentWidget() not implemented yet')
    @property
    def render_function(self):
        def createView(state, actions):
            return self._widgets[self._currentIndex].h(state, actions)
        return createView

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

class _size():
    def setHeight(self, *args): ...

class _header():
    def setSectionResizeMode(self, *args): ...
    def hide(self): ...

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
        self._element = 'div'
        self._validator = None
        self._sender = None
        self._jswindow = None
    def setWindowFlags(self, flags):
        self._flags = flags
    def setWindowTitle(self, title):
        self._title = title
    def windowTitle(self):
        return self._title
    def setLayout(self, layout):
        self._layout = layout
    @property
    def layout(self):
        return self._layout
    @layout.setter
    def layout(self, layout):
        self._layout = layout
    def _size(self):
        return {'width': 500 if 'width' not in self._style else self._style['width'],
                'height': 300 if 'height' not in self._style else self._style['height']}
    def show(self):
        if self.parent == None:   # Is an independent window
            if self._layout is None:
                raise RuntimeError('Custom top level widget has no layout')
            self._layout._styles = {**self._style, **self._framestyle}
            if QAPP is None or QAPP.window is not None:
                window_data = toObj({'title': self._title, 'dimension':self._size()})
                def createApp(content, win):
                    renderfn = create_proxy(self._layout.render_function)
                    return app(toObj({'stateid':0}), toObj({'change':create_proxy(state_change)}), renderfn, content)
                self._jswindow = window.osjs.make('osjs/window', window_data).render(createApp)
            else:
                QAPP.set_window(self)
        else:
            self._hidden = False
    def raise_(self): ...
    def text(self):
        return self._text
    def setText(self, text):
        self._text = text
    def insert(self, text):
        self._text = text
    def clear(self):
        self._text = ''
    def currentText(self):
        return self._text
    def hide(self):
        self._hidden = True
    def isVisible(self):
        return not self._hidden
    def isHidden(self):
        return self._hidden
    def setFrameStyle(self, style):
        if (style | QFrame.NoFrame) == style:
            self._framestyle = {}
        elif (style | QFrame.HLine) == style:
            self._framestyle = {'border-style':{33:'solid', 34:'outset', 36:'inset'}[style]+' none none none', 'border-color':'white'}
        elif (style | QFrame.VLine) == style:
            self._framestyle = {'border-style':'none '+{64:'solid', 66:'outset', 68:'inset'}[style]+' none none', 'border-color':'white'}
        else:
            self._framestyle = {'border-style':{17:'solid', 18:'outset', 20:'inset'}[style], 'border-color':'white'}
    def setFrame(self, value): ...
    def setStyleSheet(self, stylesheet): ...
    def setFlat(self, value): ...
    def setLineWidth(self, linewidth):
        self._framestyle.update({'border-width':f'{linewidth}px'})
    def setToolTip(self, text):
        self._toolTip = text
    def setGeometry(self, x, y, w, h):
        self._style.update({'left':x, 'top':y, 'width':w, 'height':h})
    def setEnabled(self, value):
        self._props.pop('disabled', None) if value else self._props.update({'disabled':1})
    def setDisabled(self, value):
        self.setEnabled(not value)
    def setValidator(self, validator):
        self._validator = validator
    def validator(self):
        return self._validator
    def setParent(self, parent):
        self.parent = parent
    def setWidth(self, value):
        self._style['width'] = value
    def width(self):
        return self._size()['width']
    def setHeight(self, value):
        self._style['height'] = value
    def height(self):
        return self._size()['height']
    def setMinimumWidth(self, minwidth):
        pass
    def setMaximumWidth(self, maxwidth):
        pass
    def maximumSize(self):
        return _size()
    def setMaximumSize(self, *args):
        pass
    def setMinimumSize(self, *args):
        pass
    def setSizePolicy(self, sizePolicy, *args):
        pass
    def setFixedWidth(self, width):
        pass
    def sender(self):
        return self._sender
    def resize(self, *args):
        pass
    def horizontalHeader(self):
        return _header()
    def verticalHeader(self):
        return _header()
    def setAttribute(self, attribute, value=None):
        pass
    def setAnimated(self, policy):
        pass
    def setDocumentMode(self, policy):
        pass
    def setStyleSheet(self, style):
        pass
    def font(self):
        pass
    def content(self, state, actions):
        return []
    def deleteLater(self):
        pass
    def setWindowModality(self, modal):
        pass
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

class QMenuBar(QWidget):
    def __init__(self, parent):
        super(QMenuBar, self).__init__(parent)
        self._menuitems = []
    def addMenu(self, menu):
        self._menuitems.append(menu)
    def addAction(self, action): ...

class QMainWindow(QWidget):
    def __init__(self, parent=None, flags=None):
        super(QMainWindow, self).__init__(parent)
        self._element = 'div'
        self._layout = QBoxLayout()
        self._menu = QMenuBar(self)
        self._statusbar = None
    def setCentralWidget(self, widget):
        self._layout._widgets = [widget]
        widget.parent = self
    def menuBar(self):
        return self._menu
    def setMenuBar(self, menubar):
        self._menu = menubar
    def statusBar(self):
        if self._statusbar is None:
            self._statusbar = QStatusBar(self)
        return self._statusbar
    def move(self, new_x, new_y):
        if self._jswindow is not None:
            self._jswindow.setPosition(toObj({'left':new_x, 'top':new_y}))
    def activateWindow(self): ...
    def showNormal(self): ...
    def close(self): ...

class QPushButton(QWidget):
    def __init__(self, text='', parent=None):
        super(QPushButton, self).__init__(parent)
        self._text = text
        self._element = osjsGui.Button
        self._clicked = EventProxy(self, 'onclick', self._clickedWrapper)
        self._toggled = QtCore.Signal()
        self._props = {'label':'_text'}
    def _clickedWrapper(self, fn):
        def clickWrap(event):
            fn()
        return clickWrap
    @property
    def clicked(self):
        return self._clicked
    @property
    def toggled(self):
        return self._toggled
    def setMenu(self, menu): ...
    def setCheckable(self, value): ...

class QLabel(QWidget):
    def __init__(self, text='', parent=None):
        super(QLabel, self).__init__(parent)
        self._text = text
        self._element = jswidgets.TextLabel
        self._props = {'text':'_text'}

class QLineEdit(QWidget):
    def __init__(self, text='', parent=None):
        super(QLineEdit, self).__init__(parent)
        if not isinstance(text, str):
            parent = text
            text = ''
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
    @property
    def returnPressed(self):
        return self._editingFinished
    @property
    def textEdited(self):
        return self._editingFinished
    @property
    def textChanged(self):
        return self._editingFinished
    def setPlaceholderText(self, txt): ...
    def setClearButtonEnabled(self, clearbtn): ...
    def setReadOnly(self, value):
        self._props.update({'readonly':'readonly'}) if value else self._props.pop('readonly', None) 

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
        self._currentChangedproxy = EventProxy(self, 'onchange', self._currChangeWrapper)
        self._props = {'choices':'_items'}
        self._actions['onchange'] = self._activatedWrapper(lambda v:[])
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
    def _currChangeWrapper(self, fn):
        def curIndWrap(event, value, choices):
            self._text = value
            try:
                fn(self._items.index(value))
            except TypeError:
                fn()
        return curIndWrap
    @property
    def currentIndexChanged(self):
        return self._currentChangedproxy
    def currentIndex(self):
        return self._items.index(self._text)
    @property
    def currentTextChanged(self):
        return self._currentChangedproxy
    def setCurrentIndex(self, index):
        self._text = self._items[index]
    def itemText(self, index):
        return self._items[index]
    def blockSignals(self, blocksignal): ...

class QTabWidget(QWidget):
    def __init__(self, parent=None):
        super(QTabWidget, self).__init__(parent)
        self._element = osjsGui.Tabs
        self._tabs = []
        self._tabTitles = []
        self._props = {'labels':'_tabTitles', 'grow':1, 'shrink':1}
        self._actions['onchange'] = self._currentChangedWrapper(lambda:[])
        self._currentChanged = EventProxy(self, 'onchange', self._currentChangedWrapper)
        self._index = 0
    def addTab(self, widget, title):
        self._tabs.append(widget)
        self._tabTitles.append(title)
    def currentIndex(self):
        return self._index
    def setCurrentIndex(self, index):
        self._index = index
    def tabText(self, index):
        return self._tabTitles[index]
    def setTabText(self, index, text):
        self._tabTitles[index] = text
    def _currentChangedWrapper(self, fn):
        def changeWrap(event, index, value):
            self._index = index
            self._text = value
            try:
                fn()
            except TypeError:
                fn(index)
        return changeWrap
    @property
    def currentChanged(self):
        return self._currentChanged
    def content(self, state, actions):
        return [w.h(state, actions) for w in self._tabs if w.isVisible()]
    def setTabEnabled(self, tabID, enabled):
        pass
    def isTabEnabled(self, tabID):
        return True

class QStackedWidget(QWidget):
    def __init__(self, parent=None):
        super(QStackedWidget, self).__init__(parent)
        self._pages = []
        self._index = 0
    def addWidget(self, widget):
        self._pages.append(widget)
    def setCurrentIndex(self, index):
        self._index = int(index)
    def h(self, state, actions):
        assert self._index < len(self._pages)
        return self._pages[self._index].h(state, actions)

class QMessageBox(QWidget):
    Ok = property(lambda self: 0x00000400)
    def __init__(self, parent=None):
        super(QMessageBox, self).__init__(parent)
    def show(self):
        self.exec()
    def setStandardButtons(self, buttonFlags):
        pass
    def exec(self):
        window.osjs.make('osjs/dialog', 'alert', toObj({'message':self._text, 'title':' ', 'sound':''}), create_proxy(lambda e, v, l:[]))
    def exec_(self):
        self.exec()

class QCheckBox(QWidget):
    def __init__(self, label='', parent=None):
        super(QCheckBox, self).__init__(parent)
        self._element = osjsGui.ToggleField
        self._text = label
        self._checked = False
        self._props = {'label':'_text', 'checked':'_checked'}
        self._actions['onchange'] = self._stateChangedWrapper(lambda v:[])
        self._stateChanged = EventProxy(self, 'onchange', self._stateChangedWrapper)
    def setChecked(self, checked):
        self._checked = checked
    def setCheckState(self, state):
        self._checked = state
    def isChecked(self):
        return self._checked
    def toggle(self):
        self._checked = not self._checked
    def _stateChangedWrapper(self, fn):
        def stateWrap(event, value):
            self._checked = value
            try:
                fn(value)
            except:
                pass
        return stateWrap
    @property
    def stateChanged(self):
        return self._stateChanged

class QGroupBox(QWidget):
    def __init__(self, parent=None):
        super(QGroupBox, self).__init__(parent)
        self._element = 'div'
        self._style = {'border':'1px solid black'}

class Line(QWidget):
    def __init__(self, parent=None):
        super(Line, self).__init__(parent)
        self._element = 'hr'

# Widgets needed for SampleTransmission
class QDoubleSpinBox(QWidget):
    def __init__(self, parent=None):
        super(QDoubleSpinBox, self).__init__(parent)
        self._element = jswidgets.NumberSpinner
        self._min, self._max, self._value, self._step, self._suffix = (0.0, 99.99, 0, 1.0, '')
        self._props = {'value':'_value', 'min':'_min', 'max':'_max', 'step':'_step'}
        self._textChanged = EventProxy(self, 'onchange', self._textChangedWrapper)
        self._actions['onchange'] = self._textChangedWrapper(lambda x:[])
    def setDecimals(self, value):
        pass
    def setValue(self, value):
        self._value = value
    def setMinimum(self, value):
        self._min = value
    def setMaximum(self, value):
        self._max = value
    def setSingleStep(self, value):
        self._step = value
    def setSuffix(self, value):
        self._suffix = value
    def value(self):
        return float(self._value)
    def _textChangedWrapper(self, fn):
        def Wrap(event, value):
            self._value = value
            fn(value)
        return Wrap
    @property
    def textChanged(self):
        return self._textChanged

class QTreeWidget(QWidget):
    def __init__(self, parent=None):
        super(QTreeWidget, self).__init__(parent)
        self._element = 'div'
        self._toplevelitems = []
    def setColumnCount(self, ncols):
        self._ncols = ncols
    def setHeaderLabels(self, cols):
        self._headers = cols
    def addTopLevelItem(self, item):
        self._toplevelitems.append(item)

class QTreeWidgetItem(QWidget):
    def __init__(self, parent=None):
        super(QTreeWidgetItem, self).__init__(parent)
        self._element = 'div'
        self._parent = parent
        self._isExpanded = False
        self._children = []
    def setText(self, column, text):
        self._text = text
    def setExpanded(self, value):
        self._isExpanded = value
    def addChild(self, child):
        self._children.append(child)

# Widgets needed for PyChop
class QDialog(QWidget):
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
    def exec_(self):
        self.show()

class QFileDialog(QWidget):
    def __init__(self, parent=None):
        super(QFileDialog, self).__init__(parent)

class QInputDialog(QWidget):
    def __init__(self, parent=None):
        super(QInputDialog, self).__init__(parent)

class QSpacerItem():
    def __init__(self, *args):
        pass

class QTextEdit(QWidget):
    def __init__(self, parent=None):
        super(QTextEdit, self).__init__(parent)
    def setReadOnly(self, value):
        pass

class QAction(QWidget):
    def __init__(self, name, parent=None, checkable=False):
        super(QAction, self).__init__(parent)
        self._name = name
        self._triggered = EventProxy(self, 'onclick', self._triggeredWrapper)
    def _triggeredWrapper(self, fn):
        def wrap(event):
            fn()
    @property
    def triggered(self):
        return self._triggered
    def isChecked(self):
        return False
    def setChecked(self, value): ...
    def setCheckable(self, value): ...
    def setVisible(self, value): ...
    @property
    def toggled(self):
        return self._triggered

class QActionGroup():
    def __init__(self, *args): ...
    def addAction(self, action): ...

class QMenu(QWidget):
    def __init__(self, title=None, parent=None):
        if title is not None and isinstance(title, str):
            self._title = title
        else:
            parent = title
        super(QMenu, self).__init__(parent)
        self._menuactions = []
        #self._element = osjsGui.MenubarItem
    def addMenu(self, menu): ...
    def addAction(self, action, extension=None):
        self._menuactions.append(action)
    def addSeparator(self): ...

class QSPMeta(type):
    Preferred = property(lambda self: 'preferred')
    Fixed = property(lambda self: 'fixed')
    Expanding = property(lambda self: 'expanding')

class QSizePolicy(metaclass=QSPMeta):
    def __init__(self, *args): ...

class QModelIndex():
    def __init__(self, r, c):
        self._r, self._c = (r, c)
    def row(self): return self._r
    def column(self): return self._c
    def sibling(self, row, column):
        return QModelIndex(row, column)

class _TableEventProxy(EventProxy):
    def __init__(self, *args, **kwargs):
        super(_TableEventProxy, self).__init__(*args, **kwargs)
    def connect(self, callback):
        super().connect(callback)
        self.parent._props[self.name] = self.parent._actions[self.name]

class QTableView(QWidget):
    def __init__(self, *args):
        super(QTableView, self).__init__(*args)
        self._model = None
        self._element = jswidgets.EditableTable
        self._selectionmode = QAbstractItemView.SelectItems
        self._props = {}
        self._currsel = []
        def _changeWrap(event, value=None):
            if value:
                self._model.setData(QModelIndex(value[0], value[1]), value[2])
                self._props['values'][value[1]][value[0]] = value[2]
        self._actions['onchange'] = _changeWrap
        def _selectedWrap(value):
            self._currsel = [QModelIndex(v[0], v[1]) for v in value]
        self._actions['selected'] = _selectedWrap
        def _currentCbWrap(value):
            self._props['curr_ir'], self._props['curr_ic'] = tuple(value)
        self._actions['currentcb'] = _currentCbWrap
        def _clickedWrapper(fn):
            def clickWrap(event, value=None):
                if value:
                    fn(QModelIndex(value[0], value[1]))
            return clickWrap
        self._clicked = EventProxy(self, 'clicked', _clickedWrapper)
        def _activatedWrapper(fn):
            def activatedWrap(event, value=None):
                if value:
                    fn(QModelIndex(value[0], value[1]))
            return activatedWrap
        self._activated = EventProxy(self, 'activated', _activatedWrapper)
    @property
    def clicked(self):
        return self._clicked
    @property
    def activated(self):
        return self._activated
    def setModel(self, model):
        assert hasattr(model, '_views'), 'Invalid Model'
        if self._model is not None:
            self._model._views = [v for v in self._model._views if v is not self]
        self._model = model
        model._views.append(self)
        nr, nc = (self._model.rowCount(self), self._model.columnCount(self))
        rowheaders, colheaders = ([], [])
        flags = [[self._model.flags(QModelIndex(ii, jj)) for ii in range(nr)] for jj in range(nc)]
        editable = [[(fc & Qt.ItemIsEditable) != 0 for fc in fr] for fr in flags]
        selectable = [[(fc & Qt.ItemIsSelectable) != 0 for fc in fr] for fr in flags]
        if hasattr(self._model, 'headerData'):
            for ii in range(nr):
                rowheaders.append(self._model.headerData(ii, Qt.Vertical, Qt.DisplayRole))
            for ii in range(nc):
                colheaders.append(self._model.headerData(ii, Qt.Horizontal, Qt.DisplayRole))
        data = [[self._model.data(QModelIndex(ii, jj), Qt.DisplayRole) for ii in range(nr)] for jj in range(nc)]
        self._props.update({'nr':nr, 'nc':nc, 'row_titles':rowheaders, 'col_titles':colheaders,
                            'editable':editable, 'values':data, 'onchange':create_proxy(self._actions['onchange']),
                            'col_widths':['auto']*nc, 'selectable':selectable, 'sel_mode':self._selectionmode})
    def setRootIndex(self, index):
        self.update() # This is a hack for QFileSystemModel
    def setColumnWidth(self, icol, width):
        self._props['col_widths'][icol] = f'{width*2}px'
    def setSelectionBehavior(self, value):
        self._selectionmode = value
        self._props['sel_mode'] = value
    def selectionModel(self):
        return self
    def selectedIndexes(self):
        return self._currsel
    def selectedColumns(self):
        return [QModelIndex(0, v) for v in set([ii.column() for ii in self._currsel])]
    def selectedRows(self):
        return [QModelIndex(v, 0) for v in set([ii.row() for ii in self._currsel])]
    def sortByColumn(self, column, sortmode): ... # sortmode = 0 ascending; = 1 descending
    def update(self):
        nr, nc = (self._model.rowCount(self), self._model.columnCount(self))
        self._props.update({'nr':nr, 'nc':nc})
        self._props['values'] = [[self._model.data(QModelIndex(ii, jj), Qt.DisplayRole) for ii in range(nr)] for jj in range(nc)]

class MetaQAbstractItemView(type):
    SelectRows = property(lambda self: 'selectrows')
    SelectItems = property(lambda self: 'selectitems')
    SelectColumns = property(lambda self: 'selectcolumns')
    ExtendedSelection = property(lambda self: 'extendedselection')

class QAbstractItemView(metaclass=MetaQAbstractItemView):
    def __init__(self, *args, **kwargs): ...

class QTableWidget():
    def __init__(self, *args, **kwargs): ...

class QTableWidgetItem():
    def __init__(self, *args, **kwargs): ...

class QHeaderView(QWidget):
    Stretch = property(lambda self: 'stretch')
    def __init__(self, *args):
        super(QHeaderView, self).__init__()

class QProgressDialog(QWidget):
    def __init__(self, *args):
        super(QProgressDialog, self).__init__()
    def setMinimumDuration(self, duration): ...
    def setCancelButtonText(self, canceltxt): ...
    def setRange(self, range_min, range_max): ...
    def setValue(self, value): ...
    def setLabelText(self, text): ...
    def setWindowTitle(self, title): ...
    def close(self): ...
    def wasCanceled(self):
        return False

class QStatusBar():
    def __init__(self, parent=None): ...
    def addPermanentWidget(self, widget): ...
    def setStyleSheet(self, stylesheet): ...
    def showMessage(self, stylesheet): ...

class QFileSystemModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs):
        super(QFileSystemModel, self).__init__()
        self._colheaders = ['Name', 'Date Modified', 'Type', 'Size']
        self._rootpath = None
        self._filelist = []
    def _getfilelist(self):
        with os.scandir(self._rootpath) as it:
            entries = [[e, e.is_dir(follow_symlinks=False) and not e.is_file(follow_symlinks=False), e.stat()] for e in it]
        self._filelist = []
        for ii in sorted(enumerate([e[0].name for e in entries]), key=lambda x:x[1]):
            datestr = str(datetime.date.fromtimestamp(entries[ii[0]][2].st_mtime))
            typestr = 'Folder' if entries[ii[0]][1] else f'{os.path.splitext(ii[1])[1]} File'
            self._filelist.append([ii[1], datestr, typestr, str(entries[ii[0]][2].st_size)])
    def setRootPath(self, path):
        self._rootpath = path
        self._getfilelist()
    def setNameFilters(self, filters): ...
    def setNameFilterDisables(self, disablefilters): ...
    def rowCount(self, parent):
        return len(self._filelist)
    def columnCount(self, parent):
        return 4
    def headerData(self, section, Qt_Orientation, role=None):
        if role == QtCore.Qt.DisplayRole and Qt_Orientation == QtCore.Qt.Horizontal:
            return self._colheaders[section]
    def flags(self, dummy_index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    def data(self, index, role):
        row, column = (index.row(), index.column())
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            return self._filelist[row][column]
    def index(self, path):
        self.setRootPath(path)
    def fileName(self, index):
        return self._filelist[index.row()][index.column()]
    def isDir(self, index):
        return os.path.isdir(os.path.join(self._rootpath, self.fileName(index)))

class QSplitter(QWidget):
    def __init__(self, parent=None, orientation=None):
        super(QSplitter, self).__init__()
        if parent == Qt.Horizontal or parent == Qt.Vertical:
            self._orientation = parent
            self.parent = orientation
        else:
            self.parent = parent
            self._orientation = orientation if orientation else Qt.Horizontal
        self._element = 'div'
        self._style = {'resize':self._orientation, 'overflow':'auto'}
        self._widgets = []
    def setOrientation(self, orientation):
        self._orientation = orientation
        self._style['resize'] = orientation
    def addWidget(self, widget):
        self._widgets.append(widget)
    def content(self, state, actions):
        return [w.h(state, actions) for w in self._widgets if w.isVisible()]

class QListWidgetItem(QWidget):
    def __init__(self, text=None, parent=None, *args):
        super(QListWidgetItem, self).__init__()
        if text is not None and isinstance(text, str):
            self._text = text
            self._parent = parent
        else:
            self._parent = text
        self._element = 'li'
        self._style = {'tabindex':'0'}
        self._selected = False
    def setSelected(self, selected):
        self._selected = selected
    def content(self, state, actions):
        return self._text

class QListWidget(QWidget):
    def __init__(self, parent=None):
        super(QListWidget, self).__init__(parent)
        self._items = []
        self._element = jswidgets.ListWidget
        self._props = {'items':[], 'id':id(self)} 
        def _currentCbWrap(value):
            self._props['curr_ii'] = value
        self._actions['currentcb'] = _currentCbWrap
        def _changedWrapper(fn):
            def wrap(new_selection):
                self.clearSelection()
                for it in new_selection:
                    self._items[it].setSelected(True)
                fn()
            return wrap
        self._changed = EventProxy(self, 'selectionchanged', _changedWrapper)
    def addItem(self, item):
        self._items.append(item)
        self._props['items'].append(item.text())
        if hasattr(item, '_parent'):
            item._parent = self
    def count(self):
        return len(self._items)
    def item(self, index):
        return self._items[index]
    def selectedItems(self):
        return [it for it in self._items if it._selected]
    def setSelectionMode(self, selmode): ...
    def clearSelection(self):
        for it in self._items: it.setSelected(False)
    @property
    def itemSelectionChanged(self):
        return self._changed
    def content(self, state, actions):
        # Might need to custom CSS class in inswae.css with focus background property
        # https://stackoverflow.com/questions/33246967/select-item-from-unordered-list-in-html
        return [w.h(state, actions) for w in self._items if w.isVisible()]

class QDesktopWidget():
    def __init__(self):
        pass
    def screenGeometry(self):
        return QtCore.QRect(0, 0, window.innerWidth, window.innerHeight)
