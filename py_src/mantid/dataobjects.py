class WorkspaceSingleValue:
    pass

class Workspace2D():
    def __init__(self, x, y, err, nspec=1):
        self.x, self.y, self.err, self.nspec = (x, y, err, nspec)
