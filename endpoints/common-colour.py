import json

from flask import Response
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.colour import as_rgb
from utility.image import get_image
from utility.response import BadRequest


class CommonColourHandler(Handler):

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

        image = image.convert("RGB")

        pixels = image.load()

        data = {}
        for x in range(0, image.size[0]):
            for y in range(0, image.size[1]):
                colour = as_rgb(pixels[x, y])

                value = data.get(colour)
                if not value:
                    data[colour] = 1
                else:
                    data[colour] += 1

        colours = [{"colour": key, "pixels": value} for key, value in sorted(data.items(), key=lambda item: item[1], reverse=True)]

        return Response(status=200, response=json.dumps({"status": 200, "colours": colours}), content_type="application/json")