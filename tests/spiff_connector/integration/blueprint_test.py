import json

from flask import Flask
from spiff_connector.spiff_connector_blueprint import spiff_connector_blueprint

def web_client():
    app = Flask(__name__)
    app.register_blueprint(spiff_connector_blueprint)
    web = app.test_client()
    return web

def test_blueprint_root():
    rv = web_client().get("/")
    assert rv.status == '200 OK'

def test_status():
    rv = web_client().get("/liveness")
    assert rv.status_code == 200
    # using rv.get_json() was giving me a "weakly-referenced object no longer exists". :/
    json_resp = json.loads(rv.get_data(as_text=True))
    assert (json_resp["ok"])

def test_list_commands():
    rv = web_client().get("/v1/commands")
    assert rv.status_code == 200
    # using rv.get_json() was giving me a "weakly-referenced object no longer exists". :/
    json_resp = json.loads(rv.get_data(as_text=True))
    assert(len(json_resp) == 1)
    assert(json_resp[0]["id"] == "example/CombineStrings")
    assert(len(json_resp[0]["parameters"]) == 2)
