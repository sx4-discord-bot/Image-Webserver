import json
import os
import sys

from flask import Flask, request

from utility.response import Unauthorized

config = json.load(open("config.json"))

app = Flask(__name__)

for file in os.listdir("endpoints"):
    if ".py" not in file:
        continue

    file = file[:-3]

    __import__(f"endpoints.{file}")

    app.add_url_rule(f"/api/{file}", file, getattr(sys.modules[f"endpoints.{file}"], f"{file.title()}Handler")())


@app.before_request
def before_request_check():
    pass
    #authorization = request.headers.get("authorization")
    #if not authorization:
        #return Unauthorized("Authorization header not given")

    #if authorization != config["auth"]:
        #return Unauthorized("Invalid authorization header")


@app.errorhandler(404)
def not_found(error):
    return "You've reached a dead end, turn around"


if __name__ == "__main__":
    app.run()
