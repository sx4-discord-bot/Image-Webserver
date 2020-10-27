from PIL import Image, ImageSequence

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response


class ShitHandler(SingleImageHandler):

    def on_request(self, image):
        blank = Image.new("RGBA", (763, 1000), (255, 255, 255, 0))
        background = get_image_asset("shit-meme.png")

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((185, 185)).rotate(50, expand=True)

            blank = blank.copy()
            blank.paste(frame, (215, 675), frame)
            blank.paste(background, (0, 0), background)

            frames.append(blank)

        return get_image_response(frames, transparency=255)
