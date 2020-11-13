from io import BytesIO
from math import ceil
from typing import Tuple, List, Callable

import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageSequence, UnidentifiedImageError
from flask import Response, send_file
from requests.exceptions import MissingSchema, ConnectionError

from utility.response import BadRequest

IMAGE_ASSET_PATH = "resources/images/"
FONT_ASSET_PATH = "resources/fonts/"


def get_text_array(text: str, font: ImageFont, max_width: int, width: int = 0, strip: bool = True) -> List[str]:
    text = text.strip() if strip else text

    final_lines = []

    manual_lines = text.split("\n")
    for manual_line in manual_lines:
        text_split = manual_line.split(" ")

        lines, builder = [], []
        for i, word in enumerate(text_split):
            start = 0

            if i != len(text_split) - 1:
                word += " "

            word_length, (word_width, word_height) = len(word), font.getsize(word)
            if word_width + width > max_width and word_width > max_width:
                while True:
                    cut_word = word[start:word_length]

                    cut_word_width, cut_word_height = font.getsize(cut_word)
                    if cut_word_width + width > max_width:
                        word_length -= 1
                    else:
                        if word_length == len(word):
                            builder.append(cut_word)
                            width = cut_word_width
                            break
                        elif start == 0 and width != 0:
                            builder.append(cut_word)
                            lines.append("".join(builder))
                            builder = []
                            width = 0
                            start = word_length
                            word_length = len(word)
                        else:
                            start = word_length
                            word_length = len(word)
                            lines.append(cut_word)
                            width = 0
            else:
                width += word_width
                if width > max_width:
                    lines.append("".join(builder))
                    builder = [word]
                    width = word_width
                else:
                    builder.append(word)

            if i == len(text_split) - 1 and len(builder) != 0:
                lines.append("".join(builder))

        final_lines += lines

    return final_lines


def get_text_newlined(text: str, font: ImageFont, max_width: int) -> str:
    return "\n".join(get_text_array(text, font, max_width))


def get_image(url: str, name: str = "Unknown", name_type: str = "N/A") -> Image:
    try:
        return Image.open(BytesIO(requests.get(url, stream=True).content))
    except MissingSchema:
        raise BadRequest(f"Invalid url given for the {name_type} {name}")
    except UnidentifiedImageError:
        raise BadRequest(f"The {name_type} {name} could not be formed to an image")
    except ConnectionError:
        raise BadRequest(f"Site took too long to respond for the {name_type} {name}")


def get_image_asset(path: str) -> Image:
    return Image.open(IMAGE_ASSET_PATH + path)


def get_font_asset(path: str, size: int) -> ImageFont:
    return ImageFont.truetype(FONT_ASSET_PATH + path, size)


def get_font_optimal(path: str, start: int, text: str, max_width: int) -> ImageFont:
    font = get_font_asset(path, start)
    while font.getsize(text)[0] > max_width:
        start -= 1
        font = get_font_asset(path, start)

    return font


def create_avatar(image: Image) -> Image:
    mask = Image.new("L", image.size, 0)
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
    frame_count = len(frames)
    png = frame_count == 1
    f = "png" if png else "gif"

    first_frame = frames[0]

    b = BytesIO()
    if png:
        first_frame.save(b, format=f)
    else:
        first_frame.save(b, format=f, save_all=True, append_images=frames[1:], loop=0, optimize=True, disposal=2,
                         transparency=transparency)

    b.seek(0)

    response = send_file(b, mimetype=f"image/{f}")
    response.headers["width"] = first_frame.size[0]
    response.headers["height"] = first_frame.size[1]
    response.headers["frames"] = frame_count

    return response
