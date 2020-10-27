from math import sqrt

from PIL import Image

from handlers.handler import SingleImageHandler
from utility.image import max_pixels, get_image_response, for_each_frame


class ChristmasHandler(SingleImageHandler):

    def on_request(self, image):
        final_size = max_pixels(image.size, 500)

        def parse(frame: Image) -> Image:
            frame = frame.convert("RGBA").resize(final_size)

            pixels = frame.load()
            for x in range(0, frame.size[0]):
                for y in range(0, frame.size[1]):
                    r, g, b, a = pixels[x, y]

                    o = sqrt(r ** 2 * 0.299 + g ** 2 * 0.587 + b ** 2 * 0.114)
                    o *= (o - 102) / 128
                    o = 255 - o

                    pixels[x, y] = (255, 0, 0, min(max(int(o), 0), 255))

            background = Image.new("RGBA", final_size, (255, 255, 255, 255))
            background.paste(frame, (0, 0), frame)

            return background

        return get_image_response(for_each_frame(image, parse), transparency=255)
