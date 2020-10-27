from io import BytesIO
from math import ceil
from typing import Optional, Tuple, List, Callable

import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageSequence
from flask import Response, send_file

IMAGE_ASSET_PATH = "resources/images/"
FONT_ASSET_PATH = "resources/fonts/"


def get_image(url: str) -> Image:
    return Image.open(BytesIO(requests.get(url, stream=True).content))


def get_image_asset(path: str) -> Image:
    return Image.open(IMAGE_ASSET_PATH + path)


def get_font_asset(path: str, size: int) -> ImageFont:
    return ImageFont.truetype(FONT_ASSET_PATH + path, size)


def create_avatar(image: Image) -> Image:
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)

    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    return output


def max_pixels(image_size: Tuple[int, int], max_size: int) -> Tuple[int, int]:
    width, height = image_size
    if width and height < max_size:
        return image_size

    ratio = max(width, height) / max_size
    return ceil(width / ratio), ceil(height / ratio)


def for_each_frame(image: Image, function: Callable[[type(Image)], type(Image)]) -> List[type(Image)]:
    frames = []
    for frame in ImageSequence.Iterator(image):
        frames.append(function(frame))

    return frames


def get_image_response(frames: List[type(Image)], transparency: int = 0) -> Response:
    png = len(frames) == 1
    f = "png" if png else "gif"

    first_frame = frames[0]

    b = BytesIO()
    if png:
        first_frame.save(b, format=f)
    else:
        first_frame.save(b, format=f, save_all=True, append_images=frames[1:], loop=0, optimize=True, disposal=2, transparency=transparency)

    b.seek(0)

    response = send_file(b, mimetype=f"image/{f}")
    response.headers["width"] = first_frame.size[0]
    response.headers["height"] = first_frame.size[1]

    return response
