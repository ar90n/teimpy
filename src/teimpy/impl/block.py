import numpy as np
from itertools import zip_longest, repeat

from .base import DrawerBase
from ..shape import ShapeByPixels
from .util import \
    convert_to_pil_image, \
    pad_to_multiple_of_shape, \
    get_resized_shape


def _resize(buffer, resized_shape):
    """
    Resize to displaing image size
    >>> buffer = np.arange(9).reshape(3,3).astype(np.uint8)
    >>> resized = _resize(buffer, (9, 9))
    >>> resized.shape
    (9, 9)
    """
    img = convert_to_pil_image(buffer)
    img = img.resize((resized_shape[1], resized_shape[0]))
    return np.asarray(img)


def _pack_2x1_by_half_block_code(buffer):
    """
    Pack 2x1 3 channel pixels into one half top block with bgcolor.
    >>> _pack_2x1_by_half_block_code(np.array([[[0, 255, 0]], [[255, 0, 0]]]))
    '\\x1b[48;2;255;0;0m\\x1b[38;2;0;255;0m▀'
    """
    def _pack_line(ul, ll):
        def _pack(u, l):
            res = []
            if l is not None:
                res.append('\x1b[48;2;{};{};{}m'.format(*l))
            res.append('\x1b[38;2;{};{};{}m▀'.format(*u))
            return ''.join(res)
        return ''.join([_pack(u, l) for u, l in zip(ul, ll)])

    resources = zip_longest(buffer[::2], buffer[1::2], fillvalue=repeat(None))
    res = [_pack_line(upper, lower) for upper, lower in resources]
    return '\x1b[0m\n'.join(res)


class BlockDrawer(DrawerBase):
    CELL_SHAPE = (2, 1)

    def draw(self, buffer, shape=None, preserve_aspect_ratio=True, shrink_to_terminal=True):
        if buffer.dtype not in [np.uint8]:
            raise ValueError('BlockDrawer only supports np.uin8.')
        if shape is None:
            shape = ShapeByPixels(buffer.shape[0], buffer.shape[1])
        if len(buffer.shape) == 2:
            buffer = np.repeat(buffer, 3).reshape(*buffer.shape, 3)

        resized_shape = get_resized_shape(buffer, shape, self.CELL_SHAPE, preserve_aspect_ratio, shrink_to_terminal)
        buffer = _resize(buffer, resized_shape)
        return _pack_2x1_by_half_block_code(buffer)
