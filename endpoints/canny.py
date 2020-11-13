import numpy as np

from PIL import Image
from skimage import feature
from skimage.color import rgb2gray

from handlers.handler import SingleImageHandler
from utility.image import get_image_response, for_each_frame


class CannyHandler(SingleImageHandler):

    def on_request(self, image):
        gif = image.n_frames > 1

        def parse(frame):
            canny = feature.canny(rgb2gray(np.array(frame, dtype=np.uint8)), sigma=1)
            if gif:
                canny = np.uint8(canny)

            return Image.fromarray(canny)

        return get_image_response(for_each_frame(image, parse))
