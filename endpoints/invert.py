from handlers.handler import SingleImageHandler
from utility.image import get_image_response, max_pixels, for_each_frame


class InvertHandler(SingleImageHandler):

    def on_request(self, image):
        final_size = max_pixels(image.size, 500)

        def parse(frame):
            frame = frame.convert("RGBA").resize(final_size)

            pixels = frame.load()
            for x in range(0, frame.size[0]):
                for y in range(0, frame.size[1]):
                    r, g, b, a = pixels[x, y]
                    pixels[x, y] = (255 - r, 255 - g, 255 - b, a)

            return frame

        return get_image_response(for_each_frame(image, parse), transparency=255)
