from PIL import ImageFilter

from handlers.handler import ImageFilterHandler


class EdgeHandler(ImageFilterHandler):

    def filter(self):
        return ImageFilter.FIND_EDGES
