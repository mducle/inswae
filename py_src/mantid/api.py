from collections import OrderedDict

class mtd():
    pass

class AlgorithmFactory():
    @staticmethod
    def subscribe(algorithm):
        pass

class MatrixWorkspaceProperty():
    pass

class PythonAlgorithm():
    def __init__(self):
        self._properties = OrderedDict()
        self._initialised = False
    def declareProperty(self, name, default, validator=None, doc=None):
        self._properties.update({name: [efault, validtor, doc]})
    def getPropertyValue(self, name):
        return self._properties[name]
    def __call__(self, *args, **kwargs):
        if not self._initialised:
            self.PyInit()
            self._initialised = True
        self.PyExec()
