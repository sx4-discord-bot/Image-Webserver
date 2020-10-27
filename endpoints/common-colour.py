import json

from flask import Response

from handlers.handler import SingleImageHandler
from utility.colour import as_rgb


class CommonColourHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.aliases = ["common-color"]

    def on_request(self, image):
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