class MetaQt(type):
    AlignLeft = property(lambda self: 'alignleft')
    AlignRight = property(lambda self: 'alignright')
    AlignBottom = property(lambda self: 'alignbotto')
    AlignTop = property(lambda self: 'aligntop')
    AlignCenter = property(lambda self: 'aligncenter')
    AlignHCenter = property(lambda self: 'alignhcenter')
    AlignVCenter = property(lambda self: 'alignvcenter')
    Horizontal = property(lambda self: 'horizontal')
    Vertical = property(lambda self: 'vertical')
    EditRole = property(lambda self: 'editrole')
    BackgroundRole = property(lambda self: 'editrole')
    DisplayRole = property(lambda self: 'displayrole')
    ApplicationModal = property(lambda self: 'applicationmodal')
    WA_DeleteOnClose = property(lambda self: 'wadeleteonclose')
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
    def emit(self, target):
        pass

class Signal():
    def __init__(self, *args):
        self._targets = []
    @property
    def changed(self):
        return _SignalProxy()
    def emit(self, *args):
        for t in self._targets:
            t(*args)
    def connect(self, target):
        if hasattr(target, '__call__'):
            self._targets.append(target)
        else:
            raise NotImplementedError('Only connections to callable supported')

class QAbstractTableModel():
    def __init__(self, *args): ...
    def beginResetModel(self): ...
    def endResetModel(self): ...
