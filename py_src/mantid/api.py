from micromantid.api import *
from micromantid.api import _workspaceops
import sys; sys.modules[f'{__name__}._workspaceops'] = _workspaceops