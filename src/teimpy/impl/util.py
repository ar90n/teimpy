import numpy as np
from PIL import Image


def convert_to_str(buffer):
    """
    Convert character code matrix to str.
    >>> convert_to_str(np.array([[97, 98],[99, 100]]))
    'ab\\ncd'
    """
    np_chr = np.frompyfunc(chr, 1, 1)
    return '\n'.join(np.sum(np_chr(buffer), axis=-1))


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
    mode = {
        'bool': '1',
        'uint8': 'L',
        'int32': 'I',
        'float32': 'F'
    }[str(buffer.dtype)]
    return Image.fromarray(buffer, mode=mode)
