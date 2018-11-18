from shutil import get_terminal_size

import numpy as np
from PIL import Image


from ..shape import ShapeByCells, ShapeByRatio, ShapeByPixels


def convert_to_str(buffer, eol_char='\n'):
    """
    Convert character code matrix to str.
    >>> convert_to_str(np.array([[97, 98],[99, 100]]))
    'ab\\ncd'
    """
    np_chr = np.frompyfunc(chr, 1, 1)
    return eol_char.join(np.sum(np_chr(buffer), axis=-1))


def convert_to_pil_image(buffer):
    """
    Convert numpy matrix whose dtype is supported to PIL Image.
    >>> img = convert_to_pil_image(np.array([[True]], dtype='bool'))
    >>> img.width, img.height, img.mode
    (1, 1, '1')
    >>> img = convert_to_pil_image(np.array([[0]], dtype='uint8'))
    >>> img.width, img.height, img.mode
    (1, 1, 'L')
    >>> img = convert_to_pil_image(np.array([[0]], dtype='int32'))
    >>> img.width, img.height, img.mode
    (1, 1, 'I')
    >>> img = convert_to_pil_image(np.array([[0]], dtype='float32'))
    >>> img.width, img.height, img.mode
    (1, 1, 'F')
    """
    channel = 1 if len(buffer.shape) < 3 else buffer.shape[-1]
    key = '{}_{}'.format(str(buffer.dtype), channel)
    mode = {
        'bool_1': '1',
        'uint8_1': 'L',
        'uint8_3': 'RGB',
        'int32_1': 'I',
        'float32_1': 'F'
    }[key]
    return Image.fromarray(buffer, mode=mode)


def get_diff_to_next_multiple(value, n):
    """
    Get the value which is greater equal than value and  divisible by n.
    >>> get_diff_to_next_multiple(20, 8)
    4
    """
    rem = value % n
    return 0 if rem == 0 else n - rem


def pad_to_multiple_of_shape(buffer, shape):
    """
    Padding to multiples of shape.
    >>> pad_to_multiple_of_shape(np.zeros((9, 9)), (4, 2)).shape
    (12, 10)
    """
    zero_value = False if buffer.dtype == np.bool else 0
    diff_height = get_diff_to_next_multiple(buffer.shape[0], shape[0])
    diff_width = get_diff_to_next_multiple(buffer.shape[1], shape[1])
    pad_width = [(0, diff_height), (0, diff_width)]
    if len(buffer.shape) == 3:
        pad_width.append((0, 0))
    return np.pad(buffer, pad_width, 'constant', constant_values=zero_value)


def get_termianl_pixels(cell_shape):
    """
    Get terminal size in pixels.
    """
    w, h = get_terminal_size()
    return get_pixels_of_shape(ShapeByCells(h, w), cell_shape)


def get_pixels_of_shape(shape, cell_shape, term_pixels=None):
    """
    Get shape size in pixels.
    >>> get_pixels_of_shape(ShapeByCells(10, 10), (4, 2))
    (40, 20)
    >>> get_pixels_of_shape(ShapeByRatio(0.8, 0.8), (4, 2), (50, 100))
    (40, 80)
    >>> get_pixels_of_shape(ShapeByPixels(80, 200), (4, 2))
    (80, 200)
    """
    if isinstance(shape, ShapeByCells):
        h = cell_shape[0] * shape.height
        w = cell_shape[1] * shape.width
    elif isinstance(shape, ShapeByRatio):
        term_pixels = get_termianl_pixels(cell_shape) if term_pixels is None else term_pixels
        h = int(round(shape.height * term_pixels[0]))
        w = int(round(shape.width * term_pixels[1]))
    elif isinstance(shape, ShapeByPixels):
        h = shape.height
        w = shape.width
    else:
        raise ValueError('Unknown shape format.')
    return (h, w)


def get_resized_shape(buffer, shape, cell_shape, preserve_aspect_ratio, shrink_to_terminal):
    """
    Get the shape of resized buffer.
    """
    term_pixels = get_termianl_pixels(cell_shape)
    resized_shape = get_pixels_of_shape(shape, cell_shape, term_pixels)

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

