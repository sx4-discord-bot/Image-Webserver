from PIL import ImageFilter

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_image_response, for_each_frame


class TrashHandler(SingleImageHandler):

    def on_request(self, image):
        background = get_image_asset("trash-meme.jpg")

        image = image.convert("RGBA").resize((385, 384)).filter(ImageFilter.GaussianBlur(10))

        background.paste(image, (384, 0), image)

        return get_image_response([background])
