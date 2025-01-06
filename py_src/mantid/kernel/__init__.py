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
