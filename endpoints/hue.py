import colorsys

from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image, max_pixels, get_image_response
from utility.response import BadRequest


class HueHandler(Handler):

    def __call__(self):
        image_url = self.query("image")
        if not image_url:
            return BadRequest("Image query not given")

        try:
            image = get_image(image_url)
        except MissingSchema:
            return BadRequest("Url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        final_size = max_pixels(image.size, 100)
        image = image.convert("RGBA").resize(final_size)

        frames = []
        for i in range(0, 60):
            copy = image.copy()
            pixels = copy.load()
            for x in range(0, image.size[0]):
                for y in range(0, image.size[1]):
                    r, g, b, a = pixels[x, y]

                    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                    nr, ng, nb = colorsys.hsv_to_rgb(((h * 360 + i * 6) % 360) / 360, s, v)

                    pixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)

            frames.append(copy)

        return get_image_response(frames, transparency=255)
