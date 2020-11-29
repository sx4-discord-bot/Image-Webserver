from PIL import ImageFilter

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response, for_each_frame


class TrashHandler(SingleImageHandler):

    def on_request(self, image):
        background = get_image_asset("trash-meme.png")

        filter = ImageFilter.GaussianBlur(10)

        def parse(frame):
            frame = frame.convert("RGBA").resize((193, 192)).filter(filter)

            copy = background.copy()
            copy.paste(frame, (192, 0), frame)

            return copy

        return get_image_response(for_each_frame(image, parse))
