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
    planner._style = {'width':1000, 'height':700}
    planner.show()
    return app.exec()
