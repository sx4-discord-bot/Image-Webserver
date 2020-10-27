from PIL import ImageSequence, Image

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response


class HotHandler(SingleImageHandler):

    def on_request(self, image):
        background = get_image_asset("thats-hot-meme.png")
        blank = Image.new("RGBA", background.size, (255, 255, 255, 0))

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((400, 300))

            blank = blank.copy()
            blank.paste(frame, (8, 213), frame)
            blank.paste(background, (0, 0), background)

            frames.append(blank)

        return get_image_response(frames, transparency=255)
