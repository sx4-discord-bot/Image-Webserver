from io import BytesIO

import requests
from PIL import Image
from flask import Response, send_file

from main import IMAGE_ASSET_PATH


def get_image(url) -> Image:
    return Image.open(BytesIO(requests.get(url, stream=True).content))


def get_image_asset(path) -> Image:
    return Image.open(IMAGE_ASSET_PATH + path)


def get_image_response(frames) -> Response:
    f = "png" if len(frames) == 1 else "gif"

    b = BytesIO()
    frames[0].save(b, format=f, save_all=True, append_images=frames[1:], loop=0, optimize=True, disposal=2,
                   transparency=0)
    b.seek(0)

    return send_file(b, mimetype=f"image/{f}")
