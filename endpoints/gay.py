from PIL import ImageSequence

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, max_pixels, get_image_response


class GayHandler(SingleImageHandler):

    def on_request(self, image):
        final_size = max_pixels(image.size, 500)
        overlay = get_image_asset("gay.png").resize(final_size)

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize(final_size)

            frame.paste(overlay, (0, 0), overlay)

            frames.append(frame)

        return get_image_response(frames, transparency=255)
