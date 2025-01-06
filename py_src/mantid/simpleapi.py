from . import algorithms as alg

class AnalysisDataService():
    @staticmethod
    def getObjectNames():
        return []
    @staticmethod
    def retrieveWorkspaces(ws_names):
        return []

def CreateWorkspace(*args, **kwargs):
    pass

def ConvertToPointData(*args, **kwargs):
    pass

def Rebin(*args, **kwargs):
    pass

def SetSampleMaterial(*args, **kwargs):
    pass

def CalculateSampleTransmission(*args, **kwargs):
    this_alg = alg.CalculateSampleTransmission()
    return this_alg(*args, **kwargs)
