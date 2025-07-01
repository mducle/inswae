import numpy as np

def interp1d(xp, yp, **kwargs):
    # Emulates scipy's interp1d using numpy's linear interpolation (ignore 'kind' kwargs)
    # Note that this is only accurate to about 1% compared with scipy's spline interpolation
    return lambda x: np.interp(x, xp, yp)
