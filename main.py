import traceback

from flask import Flask

from endpoints.hot import HotHandler
from endpoints.resize import ResizeHandler

BASE = "/api/{}"
IMAGE_ASSET_PATH = "resources/images/"
FONT_ASSET_PATH = "resources/fonts/"

app = Flask(__name__)
app.add_url_rule(BASE.format("hot"), "hot", HotHandler())
app.add_url_rule(BASE.format("resize"), "resize", ResizeHandler())


@app.errorhandler(404)
def not_found(error):
    return "You've reached a dead end, turn around"


if __name__ == "__main__":
    app.run()
