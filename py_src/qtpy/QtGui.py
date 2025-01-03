

class QDoubleValidator():
    pass


class QRegExpValidator():
    def __init__(self, regex, parent=None):
        self._regex = regex
    def regExp(self):
        return self._regex
    def setRegExp(self, regex):
        self._regex = regex
