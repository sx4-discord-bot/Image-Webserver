import os
import sys

from flask import Flask

from endpoints.crop import CropHandler
from endpoints.hot import HotHandler
from endpoints.resize import ResizeHandler

BASE = "/api/{}"

app = Flask(__name__)

for file in os.listdir("endpoints"):
    if ".py" not in file:
        continue

    file = file[:-3]

    app.add_url_rule(f"/api/{file}", file, getattr(sys.modules[f"endpoints.{file}"], f"{file.title()}Handler")())


@app.errorhandler(404)
def not_found(error):
    return "You've reached a dead end, turn around"


if __name__ == "__main__":
    app.run()
