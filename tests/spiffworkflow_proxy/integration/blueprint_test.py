import json

from flask import Flask
from flask.testing import FlaskClient
from spiffworkflow_proxy.blueprint import proxy_blueprint


def web_client() -> FlaskClient:
    app = Flask(__name__)
    app.register_blueprint(proxy_blueprint)
    web = app.test_client()
    return web

def test_blueprint_root() -> None:
    rv = web_client().get("/")
    assert rv.status == '200 OK'

def test_status() -> None:
    rv = web_client().get("/liveness")
    assert rv.status_code == 200
    # using rv.get_json() was giving me a "weakly-referenced object no longer exists". :/
    json_resp = json.loads(rv.get_data(as_text=True))
    assert (json_resp["ok"])

def test_list_commands() -> None:
    rv = web_client().get("/v1/commands")
    assert rv.status_code == 200
    # using rv.get_json() was giving me a "weakly-referenced object no longer exists". :/
    json_resp = json.loads(rv.get_data(as_text=True))
    assert(len(json_resp) == 1)
    assert(json_resp[0]["id"] == "example/CombineStrings")
    assert(len(json_resp[0]["parameters"]) == 2)
