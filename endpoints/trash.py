from PIL import ImageSequence, ImageFilter

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response


class TrashHandler(SingleImageHandler):

    def on_request(self, image):
        background = get_image_asset("trash-meme.jpg")

        filter = ImageFilter.GaussianBlur(10)

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((385, 384)).filter(filter)

            background = background.copy()
            background.paste(frame, (384, 0), frame)

            frames.append(background)

        return get_image_response(frames)
