from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response, for_each_frame


class FearHandler(SingleImageHandler):

    def on_request(self, image):
        background = get_image_asset("fear-meme.png")

        def parse(frame):
            frame = frame.convert("RGBA").resize((251, 251))

            copy = background.copy()
            copy.paste(frame, (260, 517), frame)

            return copy

        return get_image_response(for_each_frame(image, parse))
