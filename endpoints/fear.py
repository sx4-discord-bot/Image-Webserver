from PIL import ImageSequence

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response


class FearHandler(SingleImageHandler):

    def on_request(self, image):
        background = get_image_asset("fear-meme.png")

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((251, 251))

            background = background.copy()
            background.paste(frame, (260, 517), frame)

            frames.append(background)

        return get_image_response(frames)
