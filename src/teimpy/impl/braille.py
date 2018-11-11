from shutil import get_terminal_size

from PIL import Image
import numpy as np

from ..shape import ShapeByCells, ShapeByRatio


def _get_diff_to_next_multiple(value, n):
    """
    Get the value which is greater equal than value and  divisible by n.
    >>> _get_netx_multiple(20, 8)
    4
    """
    rem = value % n
    return 0 if rem == 0 else n - rem


def _pad_to_multiple_of_2x4(buffer):
    """
    Padding to multiple of 2x4.
    >>> _pad_to_multiple_of_2x4(np.zeros((9,9))).shape
    (12,10)
    """
    diff_height = _get_diff_to_next_multiple(buffer.shape[0], 4)
    diff_width = _get_diff_to_next_multiple(buffer.shape[1], 2)
    pad_width = [(0, diff_height), (0, diff_width)]
    return np.pad(buffer, pad_width, 'constant', constant_values=False)


def _convert_to_pillow_image(buffer):
    mode = {
        'bool': '1',
        'uint8': 'L',
        'int32': 'I',
        'float32': 'F'
    }[str(buffer.dtype)]
    return Image.fromarray(buffer, mode=mode)


def _get_resized_shape(buffer, shape, preserve_aspect_ratio, shrink_to_terminal):
    term_width, term_height = get_terminal_size()
    term_width *= 2
    term_height *= 4

    if isinstance(shape, ShapeByCells):
        w = 2 * term_height
        h = 4 * shape.height
    elif isinstance(shape, ShapeByRatio):
        w = int(round(shape.width * term_width))
        h = int(round(shape.height * term_height))
    else:
        w = shape.width
        h = shape.height

    if shrink_to_terminal:
        resized_shape = (
            min(h, term_height),
            min(w, term_width)
        )
    else:
        resized_shape = (h, w)

    if preserve_aspect_ratio:
        ver_scale = resized_shape[0] / buffer.shape[0]
        hor_scale = resized_shape[1] / buffer.shape[1]
        scale = min(ver_scale, hor_scale)
        resized_shape = (int(round(scale * buffer.shape[0])), int(round(scale * buffer.shape[1])))
    print(resized_shape)
    return resized_shape


def _resize_convert_to_binary(buffer, shape, preserve_aspect_ratio, shrink_to_terminal):
    resized_shape = _get_resized_shape(buffer, shape, preserve_aspect_ratio, shrink_to_terminal)

    img = _convert_to_pillow_image(buffer)
    img = img.resize((resized_shape[1], resized_shape[0]))
    if buffer.dtype != np.bool:
        img = img.convert('1')
    return np.asarray(img)


def _pack_2x4_pixel_to_braille_code(buffer):
    row_cells = buffer.shape[0] // 4
    col_cells = buffer.shape[1] // 2
    weights = np.array([0x01, 0x08, 0x02, 0x10, 0x04, 0x20, 0x40, 0x80])
    buffer = 0x2800 + buffer.reshape(row_cells, -1, col_cells, 2)\
        .transpose(0, 2, 1, 3).reshape(row_cells, col_cells, -1).dot(weights)
    return buffer


def _convert_to_str(buffer):
    np_chr = np.frompyfunc(chr, 1, 1)
    return '\n'.join(np.sum(np_chr(buffer), axis=-1))


def draw(buffer, shape=None, preserve_aspect_ratio=False, shrink_to_terminal=True):
    buffer = np.squeeze(buffer)
    if len(buffer.shape) != 2:
        raise ValueError('draw_with_braille only supports 1 channel image.')
    if buffer.dtype not in [np.bool, np.uint8, np.int32, np.float32]:
        raise ValueError('draw_with_braille only supports np.bool, np.uin8, np.int32 and np.float32.')

    buffer = _resize_convert_to_binary(buffer, shape, preserve_aspect_ratio, shrink_to_terminal)
    buffer = _pad_to_multiple_of_2x4(buffer)
    buffer = _pack_2x4_pixel_to_braille_code(buffer)
    return _convert_to_str(buffer)
