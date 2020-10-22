import json

from PIL import ImageSequence, Image
from flask import Response
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler


class HotHandler(Handler):

    def __call__(self, *args):
        image_url = self.request.args.get("image")
        if not image_url:
            return Response(status=400,
                            response=json.dumps({"status": 400, "message": "Image query not given"}),
                            content_type="application/json")

        try:
            image = self.get_image(image_url)
        except MissingSchema:
            return Response(status=400,
                            response=json.dumps({"status": 400, "message": "Url could not be formed to an image"}),
                            content_type="application/json")
        except ConnectionError:
            return Response(status=400,
                            response=json.dumps({"status": 400, "message": "Site took too long to respond"}),
                            content_type="application/json")

        background = self.get_image_asset("thats-hot-meme.png")
        blank = Image.new("RGBA", background.size, (255, 255, 255, 0))

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((400, 300))

            blank = blank.copy()
            blank.paste(frame, (8, 213), frame)
            blank.paste(background, (0, 0), background)

            frames.append(blank)

        return self.get_image_response(frames)