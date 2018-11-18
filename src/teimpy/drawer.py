from enum import Enum


class Mode(Enum):
    BRAILLE = 'braille'
    ITERM2_INLINE_IMAGE = 'iterm2_inline_image'
    HALD_BLOCK = 'half_block'

    def __str__(self):
        return self.value


def get_drawer(mode=Mode.BRAILLE):
    if mode == Mode.BRAILLE:
        from .impl.braille import BrailleDrawer
        return BrailleDrawer()
    elif mode == Mode.ITERM2_INLINE_IMAGE:
        from .impl.iterm2_inline_image import Iterm2InlineImageDrawer
        return Iterm2InlineImageDrawer()
    elif mode == Mode.HALD_BLOCK:
        from .impl.block import BlockDrawer
        return BlockDrawer()
    else:
        raise ValueError('Given not supported mode.')
