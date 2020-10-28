from PIL import ImageFilter

from handlers.handler import ImageFilterHandler


class EmbossHandler(ImageFilterHandler):

    def filter(self):
        return ImageFilter.EMBOSS
