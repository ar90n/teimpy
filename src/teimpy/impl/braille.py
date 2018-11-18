import numpy as np

from .base import DrawerBase
from ..shape import ShapeByPixels
from .util import \
    convert_to_str, \
    convert_to_pil_image, \
    pad_to_multiple_of_shape, \
    get_resized_shape


def _resize_and_convert_to_binary(buffer, resized_shape):
    """
    Resize to displaing image size and convert to binary
    >>> buffer = np.arange(9).reshape(3,3).astype(np.uint8)
    >>> resized = _resize_and_convert_to_binary(buffer, (9, 9))
    >>> resized.shape
    (9, 9)
    >>> resized.dtype
    dtype('bool')
    """

    img = convert_to_pil_image(buffer)
    img = img.resize((resized_shape[1], resized_shape[0]))
    if buffer.dtype != np.bool:
        img = img.convert('1')
    return np.asarray(img)


def _pack_4x2_pixel_to_braille_code(buffer):
    """
    Pack 4x2 binary pixels into one braille character.
    >>> buffer = np.array([[True, True],[False, False],[False, True],[True, False]])
    >>> _pack_4x2_pixel_to_braille_code(buffer)
    array([[10345]])
    """
    row_cells = buffer.shape[0] // 4
    col_cells = buffer.shape[1] // 2
    weights = np.array([0x01, 0x08, 0x02, 0x10, 0x04, 0x20, 0x40, 0x80])
    buffer = 0x2800 + buffer.reshape(row_cells, -1, col_cells, 2)\
        .transpose(0, 2, 1, 3).reshape(row_cells, col_cells, -1).dot(weights)
    return buffer


class BrailleDrawer(DrawerBase):
    CELL_SHAPE = (4, 2)

    def draw(self, buffer, shape=None, preserve_aspect_ratio=True, shrink_to_terminal=True):
        if len(buffer.shape) != 3 and buffer.shape[-1] == 1:
            buffer = buffer.reshape(buffer.shape[0], buffer.shape[1])
        if len(buffer.shape) != 2:
            raise ValueError('BrailleDrawer only supports 1 channel image.')
        if buffer.dtype not in [np.bool, np.uint8, np.int32, np.float32]:
            raise ValueError('BrailleDrawer only supports np.bool, np.uin8, np.int32 and np.float32.')
        if shape is None:
            shape = ShapeByPixels(buffer.shape[0], buffer.shape[1])

        resized_shape = get_resized_shape(buffer, shape, self.CELL_SHAPE, preserve_aspect_ratio, shrink_to_terminal)
        buffer = _resize_and_convert_to_binary(buffer, resized_shape)
        buffer = pad_to_multiple_of_shape(buffer, self.CELL_SHAPE)
        buffer = _pack_4x2_pixel_to_braille_code(buffer)
        return convert_to_str(buffer)
