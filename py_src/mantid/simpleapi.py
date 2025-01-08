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
    from .algorithms import CalculateSampleTransmission as this_alg
    alg_instance = this_alg()
    return alg_instance(*args, **kwargs)
