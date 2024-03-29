from typing import Tuple

from PIL import ImageColor


def as_rgb_tuple(rgb: int) -> Tuple[int, int, int]:
    return (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF


def as_rgb(rgb: Tuple[int, int, int]) -> int:
    return ((rgb[0] & 0xFF) << 16) | ((rgb[1] & 0xFF) << 8) | ((rgb[2] & 0xFF) << 0)


class Colour:

    def __new__(cls, value):
        if isinstance(value, str):
            if value.startswith("#"):
                try:
                    return int(value[1:], 16)
                except ValueError:
                    pass

            try:
                return int(value)
            except ValueError:
                pass

            colour_value = ImageColor.colormap.get(value.lower())
            if isinstance(colour_value, tuple):
                return as_rgb(colour_value)
            elif isinstance(colour_value, str):
                return int(colour_value[1:], 16)

            raise ValueError
        elif isinstance(value, int):
            return value
        elif isinstance(value, (tuple, list)):
            return as_rgb(value)
        else:
            raise ValueError
