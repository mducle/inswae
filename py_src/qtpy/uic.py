import xmltodict
import json
import os.path
import importlib
import operator
from qtpy import QtCore, QtWidgets

try:
    import js
except ModuleNotFoundError:
    from warnings import warn
else:
    def warn(msg):
        js.console.warn(msg)

def _getenum(x):
    try:
        return operator.attrgetter(x.replace('::', '.'))(QtCore)
    except AttributeError:
        return operator.attrgetter(x.replace('::', '.'))(QtWidgets)

_standardtypes = {'string':lambda x: x if isinstance(x, str) else '',
                  'bool':lambda x: True if 'true' in x else False,
                  'number':lambda x:int(x),
                  'double':lambda x:float(x),
                  'enum':_getenum}

def _gridlayoutargs(itm):
    args = {**{'row':0, 'column':0, 'rowspan':1, 'columnspan':1}, **{n[1:]:int(v) for n, v in itm.items() if n.startswith('@')}}
    return (args['row'], args['column'], args['rowspan'], args['columnspan']) 

def _loadProp(obj, props):
    if not isinstance(props, list):
        props = [props]
    for pp in props:
        pv = [v for v in pp.items()]
        try:
            setmethod = getattr(obj, 'set' + pv[0][1][0].upper() + pv[0][1][1:])
        except AttributeError:
            warn(f'Could not set property {pv[0][1]} of object {type(obj)}')
            continue
        typestr = pv[1][0]
        val = pv[1][1]
        try:
            if typestr in _standardtypes.keys():
                setmethod(_standardtypes[typestr](val))
            elif typestr == 'size':
                setmethod(int(val['width']), int(val['height']))
            elif typestr == 'rect':
                setmethod(int(val['x']), int(val['y']), int(val['width']), int(val['height']))
            else:  # Type is a Q{typestr} e.g. QSizePolicy [ignore for now]
                warn(f'Unhandled type {typestr} with value {val} in method {setmethod}')
        except TypeError:
            warn(f'Unhandled type {typestr} with value {val} in method {setmethod}')

def _addChildren(parentbase, childs, adder, argsfun=lambda x:[]):
    for itm in childs if isinstance(childs, list) else [childs]:
        if 'widget' in itm.keys() and '@class' in itm['widget'].keys():
            adder(_processWidget(parentbase, itm['widget']), *argsfun(itm))
        elif '@class' in itm.keys():
            adder(_processWidget(parentbase, itm), *argsfun(itm))
        elif 'layout' in itm.keys():
            widget = QtWidgets.QWidget()
            adder(widget, *argsfun(itm))
            _popLayout(parentbase, widget, itm['layout'])

def _popLayout(parentbase, instance, widget):
    layout = _processWidget(parentbase, widget)
    if widget['@class'] == 'QGridLayout':
        childs = _addChildren(parentbase, widget['item'], layout.addWidget, _gridlayoutargs)
    else:
        childs = _addChildren(parentbase, widget['item'], layout.addWidget)
    instance.setLayout(layout)

def _processWidget(parentbase, widget, instance=None):
    #print(f'Processing {widget["@name"]} of class: {widget["@class"]}')
    try:
        classcon = getattr(QtWidgets, widget['@class'])
    except AttributeError:
        warn(f'Could not construct widget with class < {widget["@class"]} >')
        return QtWidgets.QWidget()
    if instance is None:
        instance = classcon()
        if '@name' in widget.keys():
            setattr(parentbase, widget['@name'], instance)
    else:
        assert isinstance(instance, classcon)
    if 'property' in widget.keys():
        _loadProp(instance, widget['property'])
    if 'layout' in widget.keys():
        _popLayout(parentbase, instance, widget['layout'])
    if widget['@class'] == 'QComboBox':
        if 'item' in widget.keys():
            for itm in [v['property']['string'] for v in widget['item']]:
                instance.addItem(itm)
    elif widget['@class'] == 'QStackedWidget':
        _addChildren(parentbase, widget['widget'], instance.addWidget)
    elif widget['@class'] == 'QSplitter':
        instance.addWidget(_processWidget(parentbase, widget['widget']))
    elif widget['@class'] == 'QTabWidget':
        _addChildren(parentbase, widget['widget'], instance.addTab, lambda itm: (itm['attribute']['string'],))
    elif widget['@class'] == 'QFrame':
        thislayout = QtWidgets.QVBoxLayout()
        thislayout.addWidget(_processWidget(parentbase, widget['widget']))
        instance.setLayout(thislayout)
    elif widget['@class'] == 'QTreeWidget':
        if 'column' in widget.keys():
            cols = [v['property']['string'] for v in widget['column']]
            instance.setColumnCount(len(cols))
            instance.setHeaderLabels(cols)
    elif widget['@class'] == 'QMainWindow':
        pass
    elif 'widget' in widget.keys():
        raise RuntimeError(f'Widget {widget["@class"]} has unhandled children')
    return instance

def _processMenu(parent, widget):
    #print(f'Processing {widget["@name"]} of class: {widget["@class"]}')
    instance = getattr(QtWidgets, widget['@class'])(parent=parent)
    setattr(parent, widget['@name'], instance)
    if 'property' in widget.keys():
        _loadProp(instance, widget['property'])
    if 'widget' in widget.keys():
        for itm in widget['widget'] if isinstance(widget['widget'], list) else [widget['widget']]:
            assert itm['@class'] == 'QMenu', f'Unknown QMenuBar child class {itm["@class"]}'
            instance.addMenu(_processMenu(parent, itm))
    if 'addaction' in widget.keys():
        for itm in widget['addaction'] if isinstance(widget['addaction'], list) else [widget['addaction']]:
            try:
                instance.addAction(getattr(parent, itm['@name']))
            except TypeError: # Bug in Qt - sometimes it puts QMenus in "addaction"s
                pass
    return instance

def _create_instance(uidict, baseinstance):
    basewidget = uidict['widget']
    _processWidget(baseinstance, basewidget, baseinstance)
    menubar, statusbar = (None, None)
    if 'layout' not in basewidget:
        if isinstance(basewidget['widget'], list):
            for w in basewidget['widget']:
                if 'layout' in w.keys():
                    w0 = w
                elif w['@class'] == 'QStatusBar':
                    statusbar = w
                if w['@class'] == 'QMenuBar':
                    menubar = w
                else:
                    pass # Ignore other widgets
        else:
            w0 = basewidget['widget']
        centralwidget = _processWidget(baseinstance, w0)
        baseinstance.setCentralWidget(centralwidget)
    if 'action' in basewidget.keys():
        actions = basewidget['action'] if isinstance(basewidget['action'], list) else [basewidget['action']]
        for act in actions:
            actionobj = QtWidgets.QAction(baseinstance)
            _loadProp(actionobj, act['property'])
            setattr(baseinstance, act['@name'], actionobj)
    if menubar and hasattr(baseinstance, 'setMenuBar'):
        baseinstance.setMenuBar(_processMenu(baseinstance, menubar))
    if statusbar:
        setattr(baseinstance, statusbar['@name'], QtWidgets.QStatusBar(parent=baseinstance))
    if 'connections' in uidict and uidict['connections'] and 'connection' in uidict['connections']:
        cons = uidict['connections']['connection']
        for cn in (cons if isinstance(cons, list) else [cons]):
            sig, slot = (cn[k].split('(')[0] for k in ['signal', 'slot'])
            getattr(getattr(baseinstance, cn['sender']), sig).connect(getattr(getattr(baseinstance, cn['receiver']), slot))

def _import_customWidgets(uidict):
    if 'customwidgets' in uidict.keys():
        widgets = uidict['customwidgets']['customwidget']
        if isinstance(widgets, dict): widgets = [widgets]
        for cw in widgets:
            libname, wclass = (cw['header'].replace(r'/', '.')[:-2], cw['class'])
            cw_mod = importlib.import_module(libname)
            setattr(QtWidgets, wclass, getattr(cw_mod, wclass))
            #print(f'Loaded custom widget {wclass} from library {libname}')

class _UILoader():
    def __init__(self, uifile, baseinstance=None, noinstance=False):
        with open(uifile, 'r') as f:
            self.uidict = xmltodict.parse(f.read())
        clsname = self.uidict['ui']['class'] if 'class' in self.uidict['ui'].keys() else 'customWidget'
        _import_customWidgets(self.uidict['ui'])
        self.baseinstance = baseinstance
        classcon = getattr(QtWidgets, self.uidict['ui']['widget']['@class'])
        if baseinstance is None:
            def initfun(this, *args, **kwargs):
                this.uidict = self.uidict
            def setUi(this, win):
                _create_instance(self.uidict['ui'], win)
            self.classtype = type(clsname, (), {'__init__':initfun, 'setupUi':setUi})
            def superinitfun(this, *args, **kwargs):
                classcon.__init__(this, *args, **kwargs)
                this.uidict = self.uidict
                _create_instance(this.uidict['ui'], this)
            self.superclasstype = type(clsname, (classcon,), {'__init__':superinitfun})
            if QtWidgets.QApplication.instance() is not None:
                self.baseinstance = self.superclasstype()
        else:
            assert isinstance(baseinstance, classcon)
            _create_instance(self.uidict['ui'], self.baseinstance)

def loadUi(uifile, baseinstance=None, workingDirectory=None):
    if workingDirectory is not None:
        uifile = os.path.join(workingDirectory, uifile)
    return _UILoader(uifile, baseinstance).baseinstance

def loadUiType(uifile, from_imports=False):
    loader = _UILoader(uifile)
    return loader.classtype, loader.baseinstance

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    #import json; with open('converter.ui','r') as f: ud = xmltodict.parse(f.read()); print(json.dumps(ud, indent=2))
    #c0 = loadUi('TofConverter/converter.ui'); c0.show(); print(c0.InputVal)
    #c1 = loadUi('SampleTransmissionCalculator/SampleTransmission.ui'); c1.show(); print(c1.single_high_spin_box)
    c1 = loadUi('mainwindow.ui'); c1.show(); print('wgtSlice' in dir(c1))
    app.exec()
