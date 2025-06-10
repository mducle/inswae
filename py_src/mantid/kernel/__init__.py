from micromantid.kernel import *
import sys; sys.modules[f'{__name__}.funcinspect'] = funcinspect

class FeatureTypeMeta(type):
    Interface = property(lambda self: 'interface')
class FeatureType(metaclass=FeatureTypeMeta): ...
