import pkg_resources

from .shape import ShapeByCells, ShapeByPixels, ShapeByRatio  # noqa
from .drawer import Mode, get_drawer  # noqa

try:
    __version__ = pkg_resources.get_distribution('teimpy').version
except pkg_resources.DistributionNotFound:
    __version__ = "develop"
