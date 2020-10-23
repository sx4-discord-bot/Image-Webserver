from io import BytesIO
from typing import Optional, Tuple

import requests
from PIL import Image, ImageOps, ImageDraw
from flask import Response, send_file

IMAGE_ASSET_PATH = "resources/images/"
FONT_ASSET_PATH = "resources/fonts/"


def get_image(url: str) -> Image:
    return Image.open(BytesIO(requests.get(url, stream=True).content))


def get_image_asset(path: str) -> Image:
    return Image.open(IMAGE_ASSET_PATH + path)


def create_avatar(image: Image) -> Image:
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)

    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    return output


def get_image_response(frames: [Image], transparency: int = 0) -> Response:
    png = len(frames) == 1
    f = "png" if png else "gif"

    b = BytesIO()
    if png:
        frames[0].save(b, format=f)
    else:
        frames[0].save(b, format=f, save_all=True, append_images=frames[1:], loop=0, optimize=True, disposal=2,
                       transparency=transparency)

    b.seek(0)

    return send_file(b, mimetype=f"image/{f}")
