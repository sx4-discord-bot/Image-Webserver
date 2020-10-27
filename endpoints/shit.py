from PIL import Image

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response, for_each_frame


class ShitHandler(SingleImageHandler):

    def on_request(self, image):
        blank = Image.new("RGBA", (763, 1000), (255, 255, 255, 0))
        background = get_image_asset("shit-meme.png")

        def parse(frame):
            frame = frame.convert("RGBA").resize((185, 185)).rotate(50, expand=True)

            copy = blank.copy()
            copy.paste(frame, (215, 675), frame)
            copy.paste(background, (0, 0), background)

            return copy

        return get_image_response(for_each_frame(image, parse), transparency=255)
