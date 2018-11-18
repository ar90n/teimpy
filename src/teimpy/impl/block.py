import numpy as np

from .base import DrawerBase
from ..shape import ShapeByPixels
from .util import \
    convert_to_pil_image, \
    pad_to_multiple_of_shape, \
    get_resized_shape


def _resize(buffer, resized_shape):
    """
    Resize to displaing image size
    """
    img = convert_to_pil_image(buffer)
    img = img.resize((resized_shape[1], resized_shape[0]))
    return np.asarray(img)


def _pack_2x1_by_half_block_code(buffer):
    """
    Pack 2x1 3 channel pixels into one half top block with bgcolor.
    >>> _pack_2x1_by_half_block_code(np.array([[[0, 255, 0]], [[255, 0, 0]]]))
    '\\x1b[48;2;0;255;0m\\x1b[38;2;255;0;0m▄'
    """
    row_cells = buffer.shape[0] // 2
    col_cells = buffer.shape[1] // 1
    buffer = buffer.reshape(row_cells, -1, col_cells, 1, 3)\
        .transpose(0, 2, 1, 3, 4).reshape(row_cells, col_cells, 6)

    def _pack(v):
        return '\x1b[48;2;{};{};{}m\x1b[38;2;{};{};{}m\u2584'.format(*v)
    res = [''.join([_pack(v) for v in row]) for row in buffer]
    return '\x1b[0m\n'.join(res)


class BlockDrawer(DrawerBase):
    CELL_SHAPE = (2, 1)

    def draw(self, buffer, shape=None, preserve_aspect_ratio=True, shrink_to_terminal=True):
        if buffer.dtype not in [np.uint8]:
            raise ValueError('draw_with_braille only supports np.uin8.')
        if shape is None:
            shape = ShapeByPixels(buffer.shape[0], buffer.shape[1])
        if len(buffer.shape) == 2:
            buffer = np.repeat(buffer, 3).reshape(*buffer.shape, 3)

        resized_shape = get_resized_shape(buffer, shape, self.CELL_SHAPE, preserve_aspect_ratio, shrink_to_terminal)
        buffer = _resize(buffer, resized_shape)
        buffer = pad_to_multiple_of_shape(buffer, self.CELL_SHAPE)
        return _pack_2x1_by_half_block_code(buffer)
