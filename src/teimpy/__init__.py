import pkg_resources

from .shape import ShapeByCells, ShapeByPixels, ShapeByRatio  # noqa
from .impl import draw_with_braille, draw_with_iterm2_inline_image  # noqa

__version__ = pkg_resources.get_distribution('teimpy').version
