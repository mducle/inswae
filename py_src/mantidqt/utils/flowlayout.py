from qtpy.QtWidgets import QLayout, toObj
from pyodide.ffi import to_js
from hyperapp import h

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
    def setSpacing(self, spacing): ...
    @property
    def render_function(self):
        def createView(state, actions):
            rendered = []
            for obj in [w for w in self._widgets if w.isVisible()]:
                rendered.append(h('div', toObj({'style':toObj({'flex':'1'})}), obj.h(state, actions)))
            return h('div', toObj({'style': toObj({'display':'flex', 'flex-direction':'row', **self._styles})}), to_js(rendered))
        return createView

