from enum import Enum

from .impl.braille import BrailleDrawer
from .impl.iterm2_inline_image import Iterm2InlineImageDrawer
from .impl.block import BlockDrawer


class Mode(Enum):
    BRAILLE = 'braille'
    ITERM2_INLINE_IMAGE = 'iterm2_inline_image'
    HALF_BLOCK = 'half_block'

    def __str__(self):
        return self.value


def get_drawer(mode=Mode.BRAILLE):
    """
    Get drawer by specified mode.
    >>> drawer = get_drawer()
    >>> assert isinstance(drawer, BrailleDrawer)
    >>> drawer = get_drawer(Mode.ITERM2_INLINE_IMAGE)
    >>> assert isinstance(drawer, Iterm2InlineImageDrawer)
    >>> drawer = get_drawer(Mode.HALF_BLOCK)
    >>> assert isinstance(drawer, BlockDrawer)
    """
    if mode == Mode.BRAILLE:
        return BrailleDrawer()
    elif mode == Mode.ITERM2_INLINE_IMAGE:
        return Iterm2InlineImageDrawer()
    elif mode == Mode.HALF_BLOCK:
        return BlockDrawer()
    else:
        raise ValueError('Given not supported mode.')
