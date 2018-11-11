import pkg_resources

from .shape import ShapeByCells, ShapeByPixels, ShapeByRatio  # noqa
from .impl.braille import draw as draw_with_braille  # noqa
from .impl.iterm2_inline_image import draw as draw_with_iterm2_inline_image  # noqa

__version__ = pkg_resources.get_distribution('teimpy').version
