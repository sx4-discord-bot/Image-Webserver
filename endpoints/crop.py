from typing import Optional

from handlers.handler import SingleImageHandler
from utility.error import ErrorCode
from utility.image import get_image_response, for_each_frame
from utility.response import BadRequest


class CropHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["width", "w"], Optional[float]), (["height", "h"], Optional[float])]

    def on_request(self, image):
        image_width, image_height = image.size

        width = self.query("width", float) or self.query("w", float)
        height = self.query("height", float) or self.query("h", float)

        if not width and not height:
            raise BadRequest("width and height query not given", ErrorCode.QUERY_MISSING)

        width = width if width else image_width
        height = height if height else image_height

        if width <= 1:
            width = round(width * image_width)

        if height <= 1:
            height = round(height * image_height)

        if width < 1 or height < 1:
            raise BadRequest("width or height is a negative number", ErrorCode.INVALID_QUERY_VALUE)

        if width > image_width or height > image_height:
            raise BadRequest("width or height is larger than original width/height", ErrorCode.INVALID_QUERY_VALUE)

        width = int(width)
        height = int(height)

        left = image_width / 2 - width / 2
        upper = image_height / 2 - height / 2

        frames = for_each_frame(image, lambda frame: frame.crop((left, upper, width + left, height + upper)))

        return get_image_response(frames)
