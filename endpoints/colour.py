from PIL import Image

from handler import Handler
from utility.colour import as_rgb_tuple
from utility.image import get_image_response
from utility.number import get_int
from utility.response import BadRequest


class ColourHandler(Handler):

    def __call__(self):
        colour = get_int(self.query("colour"))
        if not colour:
            return BadRequest("colour query not given or not valid")

        width = get_int(self.query("width") or self.query("w")) or 100
        height = get_int(self.query("height") or self.query("h")) or 100

        return get_image_response([Image.new("RGB", (width, height), as_rgb_tuple(colour))])
