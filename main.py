from flask import Flask

from endpoints.hot import HotHandler
from endpoints.resize import ResizeHandler
from handler import Handler


class FlaskApp:

    def __init__(self, name):
        self.app = Flask(name)

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint, handler: Handler):
        self.app.add_url_rule(f"/api/{endpoint}", endpoint, handler)


app = FlaskApp(__name__)
app.add_endpoint("hot", HotHandler())
app.add_endpoint("resize", ResizeHandler())

if __name__ == "__main__":
    app.run()
