from shutil import get_terminal_size

import numpy as np

from .util import convert_to_str, convert_to_pil_image
from ..shape import ShapeByCells, ShapeByRatio, ShapeByPixels


def _get_diff_to_next_multiple(value, n):
    """
    Get the value which is greater equal than value and  divisible by n.
    >>> _get_diff_to_next_multiple(20, 8)
    4
    """
    rem = value % n
    return 0 if rem == 0 else n - rem


def _pad_to_multiple_of_4x2(buffer):
    """
    Padding to multiple of 4x2.
    >>> _pad_to_multiple_of_4x2(np.zeros((9,9))).shape
    (12, 10)
    """
    diff_height = _get_diff_to_next_multiple(buffer.shape[0], 4)
    diff_width = _get_diff_to_next_multiple(buffer.shape[1], 2)
    pad_width = [(0, diff_height), (0, diff_width)]
    return np.pad(buffer, pad_width, 'constant', constant_values=False)


def _get_termianl_pixels():
    """
    Get terminal size in pixels.
    """
    term_width, term_height = get_terminal_size()
    term_width *= 2
    term_height *= 4
    return term_height, term_width


def _get_pixels_of_shape(shape, term_pixels):
    """
    Get shape size in pixels.
    >>> _get_pixels_of_shape(ShapeByCells(10, 10), (50, 100))
    (40, 20)
    >>> _get_pixels_of_shape(ShapeByRatio(0.8, 0.8), (50, 100))
    (40, 80)
    >>> _get_pixels_of_shape(ShapeByPixels(80, 200), (50, 100))
    (80, 200)
    """
    if isinstance(shape, ShapeByCells):
        h = 4 * shape.height
        w = 2 * shape.width
    elif isinstance(shape, ShapeByRatio):
        h = int(round(shape.height * term_pixels[0]))
        w = int(round(shape.width * term_pixels[1]))
    elif isinstance(shape, ShapeByPixels):
        h = shape.height
        w = shape.width
    else:
        raise ValueError('Unknown shape format.')
    return (h, w)


def _get_resized_shape(buffer, shape, preserve_aspect_ratio, shrink_to_terminal):
    """
    Get the shape of resized buffer.
    """
    term_pixels = _get_termianl_pixels()
    resized_shape = _get_pixels_of_shape(shape, term_pixels)

    if shrink_to_terminal:
        resized_shape = (
            min(resized_shape[0], term_pixels[0]),
            min(resized_shape[1], term_pixels[1])
        )

    if preserve_aspect_ratio:
        ver_scale = resized_shape[0] / buffer.shape[0]
        hor_scale = resized_shape[1] / buffer.shape[1]
        scale = min(ver_scale, hor_scale)
        resized_heihgt = int(round(scale * buffer.shape[0]))
        resized_width = int(round(scale * buffer.shape[1]))
        resized_shape = (resized_heihgt, resized_width)
    return resized_shape


def _resize_and_convert_to_binary(buffer, shape, preserve_aspect_ratio, shrink_to_terminal):
    """
    Resize to displaing image size and convert to binary
    """
    resized_shape = _get_resized_shape(buffer, shape, preserve_aspect_ratio, shrink_to_terminal)

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


def draw(buffer, shape=None, preserve_aspect_ratio=True, shrink_to_terminal=True):
    buffer = np.squeeze(buffer)
    if len(buffer.shape) != 2:
        raise ValueError('draw_with_braille only supports 1 channel image.')
    if buffer.dtype not in [np.bool, np.uint8, np.int32, np.float32]:
        raise ValueError('draw_with_braille only supports np.bool, np.uin8, np.int32 and np.float32.')

    buffer = _resize_and_convert_to_binary(buffer, shape, preserve_aspect_ratio, shrink_to_terminal)
    buffer = _pad_to_multiple_of_4x2(buffer)
    buffer = _pack_4x2_pixel_to_braille_code(buffer)
    return convert_to_str(buffer)
