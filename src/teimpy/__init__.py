import os
from shutil import get_terminal_size 
from re import match
from io import BytesIO
from base64 import b64encode
from collections import namedtuple, OrderedDict

from PIL import Image
import numpy as np
import pkg_resources

__version__ = pkg_resources.get_distribution('teimpy').version


shape_by_cells = namedtuple('shape_by_cells', 'height width')
shape_by_pixels = namedtuple('shape_by_pixels', 'height width')
shape_by_percent = namedtuple('shape_by_percent', 'height width')


def _get_shape_property(shape=None):
    """
    Get item2 inline image protocol shape property.
    Default shape property is 'auto' in 'width' and 'height'.
    >>> _get_shape_property()
    {'width': 'auto', 'height': 'auto'}

    if None is given, it is converted to 'auto'.
    >>> _get_shape_property((100, None))
    {'width': 'auto', 'height': '100'}

    Given shape by cells.
    >>> _get_shape_property(shape_by_cells(30, 50))
    {'width': '50', 'height': '30'}

    Given shape by pixels.
    >>> _get_shape_property(shape_by_pixels(300, 500))
    {'width': '500px', 'height': '300px'}

    Given shape by percent.
    >>> _get_shape_property(shape_by_percent(80, 90))
    {'width': '90%', 'height': '80%'}
    """

    if shape is None:
        shape = (None, None)

    unit = ''
    if isinstance(shape, shape_by_cells):
        unit = ''
    elif isinstance(shape, shape_by_pixels):
        unit = 'px'
    elif isinstance(shape, shape_by_percent):
        unit = '%'

    width = 'auto' if shape[1] is None else '{}{}'.format(shape[1], unit)
    height = 'auto' if shape[0] is None else '{}{}'.format(shape[0], unit)
    return ('width', width), ('height', height)


def _compress_image(buffer, compression='JPEG'):
    """
    Compress array to specified format.
    >>> _compress_image(np.array([[0]]), 'JPEG')
    b'/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofH\
h0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAHwAAAQUBAQEB\
AQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJ\
xFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZW\
ZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1\
NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/APn+v//Z'
    """
    buffer = np.uint8(buffer)

    bio = BytesIO()
    Image.fromarray(buffer).save(bio, compression)
    return b64encode(bio.getvalue()).decode('utf-8')


def _is_in_tmux():
    return match('(screen|tmux)-', os.environ.get('TERM'))


def _get_osc():
    if _is_in_tmux():
        return '\x1bPtmux;\x1b\x1b]'
    return '\x1b]'


def _get_st():
    if _is_in_tmux():
        return '\a\x1b\\'
    return '\a'


def _create_message(data, properties):
    osc = _get_osc()
    properties = ''.join([';{}={}'.format(k, v) for k, v in properties.items()])
    st = _get_st()
    return '{}1337;File={}:{}{}'.format(osc, properties, data, st)


def draw_with_iterm2_inline_image(buffer, shape=None, preserve_aspect_ratio=False, compression='JPEG'):
    data = _compress_image(buffer, compression)

    shape_property = _get_shape_property(shape)
    properties = OrderedDict([
        *shape_property,
        ('size', str(len(data))),
        ('preserveAspectRatio', '1' if preserve_aspect_ratio else '0'),
        ('inline', '1'),
    ])
    return _create_message(data, properties)


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


def _get_resized_shape(buffer, shape, preserve_aspect_ratio):
    term_width, term_height = terminal_shape = get_terminal_size()
    term_width *= 2
    term_height *= 4

    if isinstance(shape, shape_by_cells):
        w = 2 * term_height
        h = 4 * shape.height
    elif isinstance(shape, shape_by_percent):
        w = int(round(shape.width * term_width))
        h = int(round(shape.height * term_height))
    else:
        w = shape.width
        h = shape.height

    resized_shape = (
        min(h, term_height),
        min(w, term_width)
    )
    if preserve_aspect_ratio:
        ver_scale = resized_shape[0] / buffer.shape[0]
        hor_scale = resized_shape[1] / buffer.shape[1]
        scale = min(ver_scale, hor_scale)
        resized_shape = (int(round(scale * buffer.shape[0])), int(round(scale * buffer.shape[1])))
    return resized_shape


def _resize_convert_to_binary(buffer, shape, preserve_aspect_ratio):
    resized_shape = _get_resized_shape(buffer, shape, preserve_aspect_ratio)

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


def draw_with_braille(buffer, shape=None, preserve_aspect_ratio=False):
    buffer = np.squeeze(buffer)
    if len(buffer.shape) != 2:
        raise ValueError('draw_with_braille only supports 1 channel image.')
    if buffer.dtype not in [np.bool, np.uint8, np.int32, np.float32]:
        raise ValueError('draw_with_braille only supports np.bool, np.uin8, np.int32 and np.float32.')

    buffer = _resize_convert_to_binary(buffer, shape, preserve_aspect_ratio)
    buffer = _pad_to_multiple_of_2x4(buffer)
    buffer = _pack_2x4_pixel_to_braille_code(buffer)
    return _convert_to_str(buffer)



import pydicom
dcm = pydicom.dcmread('./00349_1.3.12.2.1107.5.1.4.0.30000010092014521881200015564.dcm').pixel_array.astype(np.uint8)

print(draw_with_braille(dcm, shape_by_percent(0.5,0.5), True))
#print(draw_with_iterm2_inline_image(dcm, (10, 50)))
