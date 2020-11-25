from typing import Optional

from PIL import Image, ImageDraw

from handlers.handler import SingleImageHandler
from utility.image import create_avatar, get_image_response, get_image_asset, for_each_frame


class StatusHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["status"], Optional[str])]

    def on_request(self, image):
        status = self.query("status") or "online"
        status = status.lower()
        status = "offline" if status == "invisible" else "dnd" if status == "do not disturb" else status

        status_icon = get_image_asset(f"{status}.png")

        blank = Image.new("RGBA", (270, 270), (255, 255, 255, 0))

        def parse(frame):
            frame = create_avatar(frame.convert("RGBA").resize((270, 270)))

            draw = ImageDraw.Draw(frame)

            draw.ellipse((204, 204, 270, 270), fill=255)

            copy = blank.copy()
            copy.paste(frame, (0, 0), frame)
            copy.paste(status_icon, (213, 213), status_icon)

            return copy

        return get_image_response(for_each_frame(image, parse))
