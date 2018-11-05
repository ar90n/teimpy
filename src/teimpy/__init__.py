import os
from re import match
from io import BytesIO
from base64 import b64encode
from collections import namedtuple

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

    result = {}    
    result['width'] = 'auto' if shape[1] is None\
        else '{}{}'.format(shape[1], unit)
    result['height'] = 'auto' if shape[0] is None\
        else '{}{}'.format(shape[0], unit)
    return result


def _compress_image(buffer, format):
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
    Image.fromarray(buffer).save(bio,format)
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


def _create_message(data, properties='JPEG'):
    osc = _get_osc()
    properties = ''.join([';{}={}'.format(k, v) for k, v in properties.items()])
    st = _get_st()
    return '{}1337;File={}:{}{}'.format(osc, properties, data, st)


def draw(buffer, shape=None, preserve_aspect_ratio=True, compression='JPEG'):
    data = _compress_image(buffer, compression)

    shape_property = _get_shape_property(shape)
    properties = {
        **shape_property,
        'size': str(len(data)),
        'preserveAspectRatio': '1' if preserve_aspect_ratio else '0',
        'inline': '1',
    }

    return _create_message(data, properties)


buffer = np.arange(160 * 32).reshape((160, 32))
sh = shape_by_pixels(800, 800)
print(draw(buffer, sh, False))