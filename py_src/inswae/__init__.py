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
    
