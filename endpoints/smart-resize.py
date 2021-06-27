from handlers.handler import SingleImageHandler
from utility.error import ErrorCode
from utility.image import for_each_frame, resize_to_ratio, get_image_response
from utility.response import BadRequest


class SmartResize(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["w", "width"], int), (["h", "height"], int)]

    def on_request(self, image):
        size = self.query("width", int) or self.query("w", int), self.query("height", int) or self.query("h", int)

        if size[0] < 1 or size[1] < 1:
            raise BadRequest("width or height is a negative number", ErrorCode.INVALID_QUERY_VALUE)

        if size[0] > 5000 or size[1] > 5000:
            raise BadRequest("Neither width or height can be more than 5000 pixels in size",ErrorCode.INVALID_QUERY_VALUE)

        return get_image_response(for_each_frame(image, lambda frame: resize_to_ratio(frame, size)))
