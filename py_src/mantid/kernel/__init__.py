from . import funcinspect
import js

class Logger():
    @staticmethod
    def warning(message):
        js.console.warn(message)
    @staticmethod
    def error(message):
        js.console.error(message)

logger = Logger

class FeatureTypeMeta(type):
    Interface = property(lambda self: 'interface')
class FeatureType(metaclass=FeatureTypeMeta): ...

class DirectionMeta(type):
    Input = property(lambda self: 'input')
    Output = property(lambda self: 'output')
class Direction(metaclass=DirectionMeta): ...
    
class MaterialBuilder():
    pass

class StringListValidator():
    def __init__(self, values):
        self._values = values

class StringMandatoryValidator():
    pass

class UnitConversion():
    def run(self, *args):
        pass

class Elastic():
    pass

class UnitParametersMap():
    pass

class Quat():
    def __init__(self, *args):
        pass
    def __getitem__(self, index):
        return 1.0
    def __mul__(self, other):
        return self
    def __rmul__(self, other):
        return self

class V3D():
    def __init__(self, v1, v2, v3):
        pass
    def norm(self):
        return 1.0
    def __mul__(self, other):
        return self
    def __rmul__(self, other):
        return self
