import xmltodict
import json
import os.path
import warnings
from qtpy import QtWidgets

_standardtypes = {'string':lambda x: x if isinstance(x, str) else '',
                  'bool':lambda x: True if 'true' in x else False,
                  'number':lambda x:float(x),
                  'enum':lambda x:x}

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
            warnings.warn(f'Could not set property {pv[0][1]}')
            continue
        typestr = pv[1][0]
        val = pv[1][1]
        if typestr in _standardtypes.keys():
            setmethod(_standardtypes[typestr](pv[1][1]))
        elif typestr == 'rect':
            setmethod(int(val['x']), int(val['y']), int(val['width']), int(val['height']))
        else:  # Type is a Q{typestr} e.g. QSizePolicy [ignore for now]
            pass

def _addChildren(parentbase, childs, adder, argsfun=lambda x:[]):
    for itm in childs if isinstance(childs, list) else [childs]:
        if 'widget' in itm.keys() and '@class' in itm['widget'].keys():
            adder(_processWidget(parentbase, itm['widget']), *argsfun(itm))
        elif '@class' in itm.keys():
            adder(_processWidget(parentbase, itm))
        elif 'layout' in itm.keys():
            widget = QtWidgets.QWidget()
            adder(widget)
            _popLayout(parentbase, widget, itm['layout'])

def _popLayout(parentbase, instance, widget):
    layout = _processWidget(parentbase, widget)
    if widget['@class'] == 'QGridLayout':
        childs = _addChildren(parentbase, widget['item'], layout.addWidget, _gridlayoutargs)
    else:
        childs = _addChildren(parentbase, widget['item'], layout.addWidget)
    instance.setLayout(layout)

def _processWidget(parentbase, widget, instance=None):
    try:
        classcon = getattr(QtWidgets, widget['@class'])
    except AttributeError:
        warnings.warn(f'Could not construct widget with class < {widget["@class"]} >')
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
    elif widget['@class'] == 'QComboBox':
        if 'item' in widget.keys():
            for itm in [v['property']['string'] for v in widget['item']]:
                instance.addItem(itm)
    elif widget['@class'] == 'QStackedWidget':
        _addChildren(parentbase, widget['widget'], instance.addWidget)
    elif widget['@class'] == 'QTreeWidget':
        if 'column' in widget.keys():
            cols = [v['property']['string'] for v in widget['column']]
            instance.setColumnCount(len(cols))
            instance.setHeaderLabels(cols)
    return instance
    
def _create_instance(uidict, baseinstance):
    basewidget = uidict['widget']
    _processWidget(baseinstance, basewidget, baseinstance)
    if 'layout' not in basewidget:
        if isinstance(basewidget['widget'], list):
            for w in basewidget['widget']:
                if 'layout' in w.keys():
                    w0 = w
                else:
                    pass # Ignore other widgets which are menus or statusbars
        else:
            w0 = basewidget['widget']
        centralwidget = _processWidget(baseinstance, w0)
        baseinstance.setCentralWidget(centralwidget)
    if 'connections' in uidict and uidict['connections'] and 'connection' in uidict['connections']:
        cons = uidict['connections']['connection']
        for cn in (cons if isinstance(cons, list) else [cons]):
            sig, slot = (cn[k].split('(')[0] for k in ['signal', 'slot'])
            getattr(getattr(baseinstance, cn['sender']), sig).connect(getattr(getattr(baseinstance, cn['receiver']), slot))

class _UILoader():
    def __init__(self, uifile, baseinstance=None, noinstance=False):
        with open(uifile, 'r') as f:
            self.uidict = xmltodict.parse(f.read())
        clsname = self.uidict['ui']['class'] if 'class' in self.uidict['ui'].keys() else 'customWidget'
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
    c1 = loadUi('SampleTransmissionCalculator/SampleTransmission.ui'); c1.show(); print(c1.single_high_spin_box)
    app.exec()
