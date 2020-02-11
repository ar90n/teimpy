import argparse

from teimpy import get_drawer, Mode
import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="imgcat clone")
    parser.add_argument("--mode", type=Mode, default=Mode.BRAILLE, choices=list(Mode))
    parser.add_argument("src", type=str)
    args = parser.parse_args()

    image = Image.open(args.src)
    buffer = np.asarray(image)
    result = get_drawer(args.mode).draw(buffer)
    print(result)


if __name__ == "__main__":
    main()
