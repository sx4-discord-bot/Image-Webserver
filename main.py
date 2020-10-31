import inspect
import json
import os
import sys
import traceback

from flask import Flask, request, Request

from utility.response import InternalError, NotFound, MethodNotAllowed, BadRequest, JsonException

config = json.load(open("config.json"))

app = Flask(__name__)

app.endpoints = []

for file in os.listdir("endpoints"):
    if ".py" not in file:
        continue

    file = file[:-3]
    path = f"endpoints.{file}"

    __import__(path)

    for name, obj in inspect.getmembers(sys.modules[path], inspect.isclass):
        if obj.__module__ == path:
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


@app.errorhandler(JsonException)
def error_handler(error):
    return error.as_response()


@app.errorhandler(404)
def not_found(error):
    return NotFound("You've reached a dead end, turn around").as_response()


@app.errorhandler(405)
def method_not_allowed(error):
    return MethodNotAllowed(f"{request.method} is not allowed on this endpoint").as_response()


@app.errorhandler(Exception)
def error_handler(error):
    traceback.print_exc()
    return JsonException(500, "An unknown error occurred", {"error": str(error)}).as_response()


def on_json_loading_failed(x, y):
    raise BadRequest("Invalid json in body")


Request.on_json_loading_failed = on_json_loading_failed

if __name__ == "__main__":
    app.run("0.0.0.0", 8443)
