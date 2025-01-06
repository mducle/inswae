from collections import OrderedDict
from mantid.kernel import Direction
from mantid.kernel.funcinspect import lhs_info
import inspect

mtd = {}

class AlgorithmFactory():
    @staticmethod
    def subscribe(algorithm):
        pass

class MatrixWorkspaceProperty():
    def __init__(self, name, defaultValue=None, direction=Direction.Input, validator=None):
        self.name, self.defaultValue = (name, defaultValue)
        self.Direction, self.validator = (direction, validator)

class _AlgProp():
    def __init__(self, defaultValue, validator, doc, cls=None):
        self._def = defaultValue
        self._valid = validator
        self._doc = doc
        self._cls = cls
        self.value = defaultValue

class PythonAlgorithm():
    def __init__(self):
        self._properties = OrderedDict()
        self._initialised = False
    def declareProperty(self, name, defaultValue=None, validator=None, doc=None):
        if isinstance(name, str):
            self._properties.update({name: _AlgProp(defaultValue, validator, doc)})
        else:
            self._properties.update({name.name: _AlgProp(defaultValue, validator, doc, cls=name)})
    def getProperty(self, name):
        return self._properties[name]
    def getPropertyValue(self, name):
        return self._properties[name].value
    def __call__(self, *args, **kwargs):
        if not self._initialised:
            self.PyInit()
            self._initialised = True
        for ia, pp in enumerate(self._properties.items()):
            if ia < len(args):
                pp[1].value = args[ia]
            if pp[0] in kwargs.keys():
                pp[1].value = kwargs[pp[0]]
        if 'OutputWorkspace' in self._properties.keys() and 'OutputWorkspace' not in kwargs:
            lhs = lhs_info('names', inspect.currentframe().f_back.f_back)
            if len(lhs) > 0:
                self._properties['OutputWorkspace'].value = lhs[0]
        self.PyExec()
