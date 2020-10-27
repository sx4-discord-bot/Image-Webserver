from PIL import ImageSequence, ImageFilter

from handlers.handler import SingleImageHandler
from utility.image import get_image_response


class EmbossHandler(SingleImageHandler):

    def on_request(self, image):
        filter = ImageFilter.EMBOSS

        frames = []
        for frame in ImageSequence.Iterator(image):
            frames.append(frame.convert("RGBA").filter(filter))

        return get_image_response(frames)
