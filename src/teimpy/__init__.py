import pkg_resources

from .shape import ShapeByCells, ShapeByPixels, ShapeByRatio  # noqa
from .drawer import Mode, get_drawer  # noqa

__version__ = pkg_resources.get_distribution('teimpy').version
