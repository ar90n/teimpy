from io import StringIO, BytesIO
from PIL import Image
import numpy as np

from .. import libsixel
from .base import DrawerBase


class SixelDrawer(DrawerBase):
    def draw(self, buffer, shape=None, preserve_aspect_ratio=True):
        if buffer.dtype not in [np.uint8]:
            raise ValueError("BlockDrawer only supports np.uin8.")

        height, width = buffer.shape[0], buffer.shape[1]
        bytes = buffer.tobytes()
        if len(buffer.shape) == 3:
            dither = libsixel.sixel_dither_new(256)
            libsixel.sixel_dither_initialize(
                dither, bytes, width, height, libsixel.SIXEL_PIXELFORMAT_RGB888
            )
        else:
            dither = libsixel.sixel_dither_get(libsixel.SIXEL_BUILTIN_G8)
            libsixel.sixel_dither_set_pixelformat(dither, libsixel.SIXEL_PIXELFORMAT_G8)

        s = BytesIO()
        output = libsixel.sixel_output_new(lambda data, s: s.write(data), s)
        libsixel.sixel_encode(bytes, width, height, 1, dither, output)
        return s.getvalue().decode("ascii")
