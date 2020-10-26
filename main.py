import inspect
import json
import os
import sys

from flask import Flask, request

from utility.response import Unauthorized, InternalError, NotFound

config = json.load(open("config.json"))

app = Flask(__name__)

app.endpoints = []

for file in os.listdir("endpoints"):
    if ".py" not in file:
        continue

    file = file[:-3]

    __import__(f"endpoints.{file}")

    for name, obj in inspect.getmembers(sys.modules[f"endpoints.{file}"]):
        if inspect.isclass(obj) and name != "Handler" and "Handler" in name:
            handler = obj(app)

            app.endpoints.append(handler)
            app.add_url_rule(f"/api/{handler.name}", handler.name, handler)

            for alias in handler.aliases:
                app.add_url_rule(f"/api/{alias}", alias, handler)

            break


@app.before_request
def before_request_check():
    pass
    # authorization = request.headers.get("authorization")
    # if not authorization:
    # return Unauthorized("Authorization header not given")

    # if authorization != config["auth"]:
    # return Unauthorized("Invalid authorization header")


@app.errorhandler(404)
def not_found(error):
    return NotFound("You've reached a dead end, turn around")


@app.errorhandler(500)
def internal_error(error):
    return InternalError("An internal error occurred please report this to the developers")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443)
