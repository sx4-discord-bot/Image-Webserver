import json

from PIL import ImageStat
from flask import Response

from handlers.handler import SingleImageHandler
from utility.colour import as_rgb


class AverageColourHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.aliases = ["average-color"]

    def on_request(self, image):
        mask = None
        try:
            mask = image.getchannel("A")
        except ValueError:
            pass

        stat = ImageStat.Stat(image, mask=mask)
        return Response(status=200, response=json.dumps({"status": 200, "colour": as_rgb(tuple(int(x) for x in stat.average))}), content_type="application/json")