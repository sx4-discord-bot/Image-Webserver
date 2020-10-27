from PIL import ImageFilter

from handlers.handler import SingleImageHandler
from utility.image import get_image_response, for_each_frame


class EdgeHandler(SingleImageHandler):

    def on_request(self, image):
        filter = ImageFilter.FIND_EDGES

        frames = for_each_frame(image, lambda frame: frame.convert("RGBA").filter(filter))

        return get_image_response(frames)
