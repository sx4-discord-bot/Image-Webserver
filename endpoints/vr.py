from PIL import Image

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response, for_each_frame


class VrHandler(SingleImageHandler):

    def on_request(self, image):
        background = get_image_asset("vr.png")
        blank = Image.new("RGBA", background.size, (255, 255, 255, 0))

        def parse(frame):
            frame = frame.convert("RGBA").resize((225, 135))

            copy = blank.copy()
            copy.paste(frame, (15, 300), frame)
            copy.paste(background, (0, 0), background)

            return copy

        return get_image_response(for_each_frame(image, parse), transparency=255)
