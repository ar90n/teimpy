from io import StringIO, BytesIO
from sixel import SixelWriter
from PIL import Image

from .base import DrawerBase


class SixelDrawer(DrawerBase):
    def draw(self, buffer, shape=None, preserve_aspect_ratio=True):
        input = BytesIO()
        img = Image.fromarray(buffer)
        img.save(input, "PNG")
        input.seek(0)

        output = StringIO()
        output.fileno = lambda: 1  # Hack for PySixel

        SixelWriter().draw(input, output=output)
        return output.getvalue()
