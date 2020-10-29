from PIL import Image

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, for_each_frame, get_image_response


class BeautifulHandler(SingleImageHandler):

    def on_request(self, image: Image):
        background = get_image_asset("beautiful.png")

        def parse(frame):
            frame = frame.convert("RGBA").resize((90, 104)).rotate(1, expand=True)

            copy = background.copy()
            copy.paste(frame, (253, 25), frame)
            copy.paste(frame, (256, 222), frame)

            return copy

        return get_image_response(for_each_frame(image, parse), transparency=255)
