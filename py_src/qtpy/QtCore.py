import inspect
import os

class MetaQt(type):
    AlignLeft = property(lambda self: 'alignleft')
    AlignRight = property(lambda self: 'alignright')
    AlignBottom = property(lambda self: 'alignbotto')
    AlignTop = property(lambda self: 'aligntop')
    AlignCenter = property(lambda self: 'aligncenter')
    AlignHCenter = property(lambda self: 'alignhcenter')
    AlignVCenter = property(lambda self: 'alignvcenter')
    AscendingOrder = property(lambda self: 'ascendingorder')
    DescendingOrder = property(lambda self: 'descendingorder')
    Horizontal = property(lambda self: 'horizontal')
    Vertical = property(lambda self: 'vertical')
    EditRole = property(lambda self: 'editrole')
    BackgroundRole = property(lambda self: 'editrole')
    DisplayRole = property(lambda self: 'displayrole')
    ApplicationModal = property(lambda self: 'applicationmodal')
    WA_DeleteOnClose = property(lambda self: 'wadeleteonclose')
    WA_TransparentForMouseEvents = property(lambda self: 'watransparentformouseevents')
    ItemIsEditable = property(lambda self: 0b1)
    ItemIsEnabled = property(lambda self: 0b10)
    ItemIsSelectable = property(lambda self: 0b100)

class Qt(metaclass=MetaQt):
    def __init__(self):
        pass

class QRegExp():
    def __init__(self, regexp):
        self._regex = regexp

class QProcess():
    def __init__(self, parent=None):
        self.parent = parent
    def close(self):
        pass
    def waitForFinished(self):
        pass

class QEventLoop():
    def exec_(self): ...

class _SignalProxy():
    def __init__(self, *args):
        pass
    def emit(self, *args):
        pass

class Signal():
    def __init__(self, *args):
        self._targets = []
        self._args = args
    @property
    def changed(self):
        return _SignalProxy()
    def emit(self, *args):
        frm, caller = (inspect.currentframe().f_back, None)
        if len(frm.f_code.co_varnames) > 0:
            caller = frm.f_locals[frm.f_code.co_varnames[0]]
        for t in self._targets:
            if caller is not None and hasattr(t, '__self__') and hasattr(t.__self__, '_sender'):
                t.__self__._sender = caller
            try:
                t(*args)
            except TypeError:
                try:
                    t()
                except TypeError:
                    t(*args)
    def connect(self, target):
        if hasattr(target, '__call__'):
            self._targets.append(target)
        else:
            raise NotImplementedError('Only connections to callable supported')

class QAbstractTableModel():
    def __init__(self, *args):
        self._dataChanged = _SignalProxy()
        self._views = []
    def beginResetModel(self): ...
    def endResetModel(self):
        [v.update() for v in self._views]
    @property
    def dataChanged(self):
        return self._dataChanged

class QDir():
    def __init__(self, directory):
        self._dir = directory
    def exists(self):
        return os.path.exists(self._dir)
    def absolutePath(self):
        return os.path.abspath(self._dir)
    def cdUp(self):
        self._dir = os.path.join(self._dir, '..')
    def cd(self, path):
        self._dir = os.path.join(self._dir, path)

class MetaQLocale(type):
    RejectGroupSeparator = property(lambda self: 'rejectgroupseparator')
    C = property(lambda self: 'C')

class QLocale(metaclass=MetaQLocale):
    def __init__(self, locale_string): ...
    def setNumberOptions(self, numberoption): ...

class QMutex():
    def __init__(self): ...

class QMutexLocker():
    def __init__(self, mutex): ...

class QFileInfo():
    def __init__(self, filename):
        self._file = filename
    def isFile(self):
        return os.path.isfile(self._file)

class QObject():
    def __init__(self): ...
