class _QValidMeta(type):
    Acceptable = property(lambda self: 'acceptable')
    Intermediate = property(lambda self: 'intermediate')
    Invalid = property(lambda self: 'invalid')

class QValidator(metaclass=_QValidMeta):
    pass

class QDoubleValidator():
    def __init__(self, *args):
        if len(args) == 0:
            self._min, self._max, self._dp, self._parent = (-1e308, 1e308, 16, None)
        elif len(args) < 3:
            self._min, self._max, self._dp, self._parent = (-1e308, 1e308, 16, args[0])
        else:
            self._min, self._max, self._dp, self._parent = tuple(args)
    def validate(self, value, pos):
        try:
            x = float(value)
        except ValueError:
            return [QValidator.Invalid]
        return [QValidator.Acceptable if x >= self._min and x <= self._max else QValidator.Intermediate]
    def setBottom(self, value):
        self._min = value
    def setLocale(self, locale): ...

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
