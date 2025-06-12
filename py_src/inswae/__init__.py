def create_QE_app():
    from qtpy.QtWidgets import QApplication
    from mantidqtinterfaces.QECoverage.QECoverageGUI import QECoverageGUI
    app = QApplication([])
    mainForm = QECoverageGUI(None, None)
    mainForm._style = {'width':770, 'height':610}
    mainForm.show()
    return app.exec()

def createTofConverter():
    from qtpy.QtWidgets import QApplication
    from mantidqtinterfaces.TofConverter import converterGUI
    app = QApplication([])
    reducer = converterGUI.MainWindow(None, None)
    reducer.show()
    return app.exec()

def createSampleTransmission():
    from qtpy.QtWidgets import QApplication
    from mantidqtinterfaces.SampleTransmissionCalculator import stc_gui
    app = QApplication([])
    planner = stc_gui.SampleTransmissionCalculator(None, None)
    planner._style = {'width':1000, 'height':750}
    planner.show()
    return app.exec()

def create_pychop():
    from qtpy.QtWidgets import QApplication
    from mantidqtinterfaces.PyChop import PyChopGui
    app = QApplication([])
    window = PyChopGui.PyChopGui(None, None)
    window._style = {'width':950, 'height':650}
    window.show()
    return app.exec()

def create_dgsplanner():
    from qtpy.QtWidgets import QApplication
    from mantidqtinterfaces.DGSPlanner import DGSPlannerGUI
    app = QApplication([])
    planner = DGSPlannerGUI.DGSPlannerGUI(None, None)
    planner._style = {'width':1350, 'height':850}
    planner.show()
    return app.exec()

def createMSlice():
    from qtpy.QtWidgets import QApplication
    from mslice.app.mainwindow import MainWindow
    app = QApplication([])
    window = MainWindow(False)
    window._style = {'width':950, 'height':650}
    window.show()
    return app.exec()
