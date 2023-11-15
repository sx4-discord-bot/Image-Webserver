import json

from PIL import ImageStat
from flask import Response

from handlers.handler import SingleImageHandler
from utility.colour import as_rgb


class MedianColourHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.aliases = ["median-color"]

    def on_request(self, image):
        mask = None
        try:
            mask = image.getchannel("A")
        except ValueError:
            pass

        stat = ImageStat.Stat(image.convert("RGB"), mask=mask)
        return Response(status=200, response=json.dumps({"status": 200, "colour": as_rgb(tuple(int(x) for x in stat.median))}), content_type="application/json")