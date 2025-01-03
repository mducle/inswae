def create_QE_app():
    try:
        from qtpy.QtWidgets import QApplication
        from .QECoverageGUI import QECoverageGUI
    except:
        from pyodide.ffi import JsException
        raise JsException("Python bootstrap incomplete")
    else:
        app = QApplication([])
        mainForm = QECoverageGUI(None, None)
        mainForm.show()
        return app.exec()

