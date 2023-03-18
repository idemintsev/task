from flask import Flask

from main.settings import Config
from main.urls import urls_rules


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    [app.add_url_rule(**rule) for rule in urls_rules]

    return app
