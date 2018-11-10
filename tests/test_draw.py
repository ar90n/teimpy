import pytest
import numpy as np

import teimpy


@pytest.fixture(scope='session', params=[
    ('JPEG', '\x1bPtmux;\x1b\x1b]1337;File=;width=auto;height=auto;size=444;pre\
serveAspectRatio=1;inline=1:/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQg\
KDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAA\
EBAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9A\
QIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RF\
RkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW\
2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/APn+v//Z\
\x07\x1b\\'),
    ('PNG', '\x1bPtmux;\x1b\x1b]1337;File=;width=auto;height=auto;size=92;prese\
rveAspectRatio=1;inline=1:iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQ\
VR4nGNgAAAAAgABSK+kcQAAAABJRU5ErkJggg==\x07\x1b\\'),
])
def commpression_data(request):
    return {
        'buffer': np.array([[0]]),
        'compression': request.param[0],
        'expected': request.param[1]
    }


def test_draw_item2_inline_image(commpression_data):
    
    actual = teimpy.draw_with_iterm2_inline_image(commpression_data['buffer'], compression=commpression_data['compression'])

    assert actual == commpression_data['expected']
