import os
from re import match
from io import BytesIO
from base64 import b64encode
from collections import OrderedDict

from PIL import Image
import numpy as np

from .base import DrawerBase
from ..shape import ShapeByCells, ShapeByPixels, ShapeByRatio


def _get_shape_property(shape=None):
    """
    Get item2 inline image protocol shape property.
    Default shape property is 'auto' in 'width' and 'height'.
    >>> _get_shape_property()
    (('width', 'auto'), ('height', 'auto'))

    if None is given, it is converted to 'auto'.
    >>> _get_shape_property((100, None))
    (('width', 'auto'), ('height', '100'))

    Given shape by cells.
    >>> _get_shape_property(ShapeByCells(30, 50))
    (('width', '50'), ('height', '30'))

    Given shape by pixels.
    >>> _get_shape_property(ShapeByPixels(300, 500))
    (('width', '500px'), ('height', '300px'))

    Given shape by percent.
    >>> _get_shape_property(ShapeByRatio(80, 90))
    (('width', '90%'), ('height', '80%'))
    """

    if shape is None:
        shape = (None, None)

    unit = ''
    if isinstance(shape, ShapeByCells):
        unit = ''
    elif isinstance(shape, ShapeByPixels):
        unit = 'px'
    elif isinstance(shape, ShapeByRatio):
        unit = '%'

    width = 'auto' if shape[1] is None else '{}{}'.format(shape[1], unit)
    height = 'auto' if shape[0] is None else '{}{}'.format(shape[0], unit)
    return ('width', width), ('height', height)


def _compress_image(buffer, compression='JPEG'):
    """
    Compress array to specified format.
    >>> _compress_image(np.array([[0]]), 'JPEG')
    '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofH\
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


class Iterm2InlineImageDrawer(DrawerBase):

    def draw(self, buffer, shape=None, preserve_aspect_ratio=True, compression='JPEG'):
        data = _compress_image(buffer, compression)

        shape_property = _get_shape_property(shape)
        properties = OrderedDict([
            *shape_property,
            ('size', str(len(data))),
            ('preserveAspectRatio', '1' if preserve_aspect_ratio else '0'),
            ('inline', '1'),
        ])
        return _create_message(data, properties)
