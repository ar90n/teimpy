import os
import urllib.request

ARCHIVE_FILE = "libsixel-1.8.6.tar.gz"
LIBSIXEL_DIR = "sixel-1.8.6"


def build(setup_kwargs):
    url = f"https://github.com/saitoha/libsixel/releases/download/v1.8.6/{ARCHIVE_FILE}"
    urllib.request.urlretrieve(url, f"./{ARCHIVE_FILE}")

    commands = f"""tar -zxvf {ARCHIVE_FILE} && \
cd {LIBSIXEL_DIR} && \
./configure && \
make -j && \
cp ./src/.libs/libsixel.so ../src/teimpy/libsixel/libsixel.so
"""

    os.system(commands)
    setup_kwargs.update(
        {
            "ext_modules": EmptyListWithLength(),
            "package_data": {"": ["libsixel/libsixel.so"]},
            "include_package_data": True,
        }
    )


# from opencv-python
class EmptyListWithLength(list):
    def __len__(self):
        return 1
