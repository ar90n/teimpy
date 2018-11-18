import pytest
import numpy as np

from teimpy import get_drawer, Mode


@pytest.fixture(scope='session', params=[
    (Mode.ITERM2_INLINE_IMAGE, {'compression': 'JPEG'}, '\x1bPtmux;\x1b\x1b]1337;File=;width=auto;height=auto;size=444;pre\
serveAspectRatio=1;inline=1:/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQg\
KDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAA\
EBAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9A\
QIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RF\
RkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW\
2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/APn+v//Z\
\x07\x1b\\'),
    (Mode.ITERM2_INLINE_IMAGE, {'compression': 'PNG'}, '\x1bPtmux;\x1b\x1b]1337;File=;width=auto;height=auto;size=92;prese\
rveAspectRatio=1;inline=1:iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQ\
VR4nGNgAAAAAgABSK+kcQAAAABJRU5ErkJggg==\x07\x1b\\'),
    (Mode.BRAILLE, {}, '\u2800')
])
def setup(request):
    return {
        'buffer': np.array([[0]], dtype=np.uint8),
        'mode': request.param[0],
        'param': request.param[1],
        'expected': request.param[2]
    }


def test_draw_item2_inline_image(setup):
    drawer = get_drawer(setup['mode'])
    actual = drawer.draw(setup['buffer'], **setup['param'])

    assert actual == setup['expected']
