from typing import Optional

from handlers.handler import SingleImageHandler
from utility.error import ErrorCode
from utility.image import get_image_response, for_each_frame
from utility.response import BadRequest


class ResizeHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["image"], str), (["width", "w"], Optional[float]), (["height", "h"], Optional[float])]

    def on_request(self, image):
        width = self.query("width", float) or self.query("w", float)
        height = self.query("height", float) or self.query("h", float)

        if not width and not height:
            raise BadRequest("width and height query not given", ErrorCode.QUERY_MISSING)

        width = width if width else image.size[0]
        height = height if height else image.size[1]

        if width <= 1:
            width = round(width * image.size[0])

        if height <= 1:
            height = round(height * image.size[1])

        if width < 1 or height < 1:
            raise BadRequest("width or height is a negative number", ErrorCode.INVALID_QUERY_VALUE)

        frames = for_each_frame(image, lambda frame: frame.resize((int(width), int(height))))

        return get_image_response(frames)
