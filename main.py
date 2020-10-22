from flask import Flask

from endpoints.hot import HotHandler
from handler import Handler


class FlaskApp:

    def __init__(self, name):
        self.app = Flask(name)

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler: Handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler)


app = FlaskApp(__name__)
app.add_endpoint("/hot", "hot", HotHandler())

if __name__ == "__main__":
    app.run()
