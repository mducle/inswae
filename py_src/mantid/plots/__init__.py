# This file should be left free of PyQt imports to allow quick importing
# of the main package.
from collections.abc import Iterable  # noqa: F401
#from matplotlib.projections import register_projection
#from matplotlib.scale import register_scale

from mantid.plots import datafunctions, axesfunctions#, axesfunctions3D  # noqa: F401
#from mantid.plots.legend import LegendProperties  # noqa: F401
from mantid.plots.datafunctions import get_normalize_by_bin_width  # noqa: F401
#from mantid.plots.scales import PowerScale, SquareScale
#from mantid.plots.mantidaxes import MantidAxes, MantidAxes3D, WATERFALL_XOFFSET_DEFAULT, WATERFALL_YOFFSET_DEFAULT  # noqa: F401
from mantid.plots.utility import artists_hidden, autoscale_on_update, convert_color_to_hex, legend_set_draggable, MantidAxType  # noqa: F401

#register_projection(MantidAxes)
#register_projection(MantidAxes3D)
#register_scale(PowerScale)
#register_scale(SquareScale)
