class _QValidMeta(type):
    Acceptable = property(lambda self: 'acceptable')
    Intermediate = property(lambda self: 'intermediate')

class QValidator(metaclass=_QValidMeta):
    pass

class QDoubleValidator():
    def __init__(self, *args):
        self._value = 0.0 if len(args) == 0 else (args[0] if len(args) < 3 else args[2])

class QRegExpValidator():
    def __init__(self, regex='', parent=None):
        self._regex = regex
    def regExp(self):
        return self._regex
    def setRegExp(self, regex):
        self._regex = regex

class QFontMetrics():
    def __init__(self, font):
        pass
    def width(self, *args):
        return 1
