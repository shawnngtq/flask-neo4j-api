import os

from flask import (
    Flask, jsonify
)

from . import config
from . import models


def create_app():
    print(os.listdir())
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    models.init_app(app)

    @app.route("/hello")
    def hello():
        return {
            "message": "hello world"
        }

    @app.route("/hello2")
    def hello2():
        return jsonify(["hello world"])

    return app
