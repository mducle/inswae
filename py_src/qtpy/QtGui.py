class QDoubleValidator():
    def __init__(self, value=0.0, parent=None):
        self._value = value

class QRegExpValidator():
    def __init__(self, regex='', parent=None):
        self._regex = regex
    def regExp(self):
        return self._regex
    def setRegExp(self, regex):
        self._regex = regex
