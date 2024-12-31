class MetaQt(type):
    @property
    def AlignLeft(self): 
        return 1
    @property
    def AlignRight(self):
        return 2
    @property
    def AlignBottom(self):
        return 3
    @property
    def AlignTop(self):
        return 4
    @property
    def AlignCenter(self):
        return 5
    @property
    def AlignHCenter(self):
        return 6
    @property
    def AlignVCenter(self):
        return 7

class Qt(metaclass=MetaQt):
    def __init__(self):
        pass

class QRegExp():
    pass

class QProcess():
    pass
