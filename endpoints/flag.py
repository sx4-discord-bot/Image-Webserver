from io import BytesIO

import requests
from PIL import Image

from handlers.handler import SingleImageHandler
from utility.image import get_image_response, max_pixels, for_each_frame
from utility.response import BadRequest


class FlagHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["flag"], str)]

    def on_request(self, image):
        flag = self.query("flag")

        flag_response = requests.get(f"http://www.geonames.org/flags/x/{flag}.gif", stream=True)

        if flag_response.status_code == 404:
            raise BadRequest("Invalid flag code")

        final_size = max_pixels(image.size, 200)
        flag_image = Image.open(BytesIO(flag_response.content)).convert("RGBA").resize(final_size)

        def parse(frame):
            frame = frame.convert("RGBA").resize(final_size)

            return Image.blend(frame, flag_image, 0.35)

        return get_image_response(for_each_frame(image, parse), transparency=255)
