from typing import List, Any

from PIL import Image

from handlers.handler import MultipleImageHandler
from utility.image import get_image_asset, get_image_response


class WhoWouldWinHandler(MultipleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["first_image", str]), (["second_image"], str)]

    def on_request(self, images: List[type(Image)]):
        first_image, second_image = images

        background = get_image_asset("www.png")

        background.paste(first_image, (30, 180), first_image)
        background.paste(second_image, (510, 180), second_image)

        return get_image_response([background])

    def image_queries(self) -> List[str]:
        return ["first_image", "second_image"]

    def modify_images(self, images: List[type(Image)]) -> Any:
        return [image.convert("RGBA").resize((400, 400)) for image in images]
