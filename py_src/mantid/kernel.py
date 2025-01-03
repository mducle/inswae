import js

class logger():
    @staticmethod
    def warning(message):
        js.console.log(f'Warning: {message}')

class FeatureTypeMeta(type):
    Interface = property(lambda self: 'interface')

class FeatureType(metaclass=FeatureTypeMeta):
    pass 
