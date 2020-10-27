from math import sqrt

from handlers.handler import SingleImageHandler
from utility.image import max_pixels, get_image_response, for_each_frame


class HalloweenHandler(SingleImageHandler):

    def on_request(self, image):
        final_size = max_pixels(image.size, 500)

        def parse(frame):
            frame = frame.convert("RGBA").resize(final_size)

            pixels = frame.load()
            for x in range(0, frame.size[0]):
                for y in range(0, frame.size[1]):
                    r, g, b, a = pixels[x, y]

                    o = sqrt(r ** 2 * 0.299 + g ** 2 * 0.587 + b ** 2 * 0.114)
                    o *= (o - 102) / 128

                    pixels[x, y] = (min(max(int(o), 0), 255), min(max(int((o - 10) / 2), 0), 255), 0, a)

            return frame

        return get_image_response(for_each_frame(image, parse), transparency=255)
