from typing import Tuple


def as_rgb_tuple(rgb: int) -> Tuple[int, int, int]:
    return (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF


def as_rgb(rgb: Tuple[int, int, int]) -> int:
    return ((rgb[0] & 0xFF) << 16) | ((rgb[1] & 0xFF) << 8) | ((rgb[2] & 0xFF) << 0)
