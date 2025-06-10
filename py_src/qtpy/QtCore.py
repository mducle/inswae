class MetaQt(type):
    AlignLeft = property(lambda self: 'alignleft')
    AlignRight = property(lambda self: 'alignright')
    AlignBottom = property(lambda self: 'alignbotto')
    AlignTop = property(lambda self: 'aligntop')
    AlignCenter = property(lambda self: 'aligncenter')
    AlignHCenter = property(lambda self: 'alignhcenter')
    AlignVCenter = property(lambda self: 'alignvcenter')

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
