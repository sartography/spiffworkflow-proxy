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
    commands_by_id = {command["id"]: command for command in json_resp}
    assert(set(commands_by_id.keys()) == {"example/AsyncBodyStatus", "example/CombineStrings"})
    assert(len(commands_by_id["example/CombineStrings"]["parameters"]) == 2)


def test_do_command_ignores_spiff_params() -> None:
    payload = {
        "arg1": "hello",
        "arg2": "world",
        "spiff__process_instance_id": 123,
        "spiff__task_id": "task-1",
        "spiff__callback_url": "http://localhost/callback",
        "spiff__task_data": {"example": True},
    }

    rv = web_client().post("/v1/do/example/CombineStrings", json=payload)

    assert rv.status_code == 200
    json_resp = json.loads(rv.get_data(as_text=True))
    assert json_resp["command_response"]["body"]["command_response"]["arg1"] == "hello"
    assert json_resp["command_response"]["body"]["command_response"]["arg2"] == "world"


def test_async_command_always_returns_accepted_status() -> None:
    payload = {
        "upstream_status": 500,
        "spiff__callback_url": "http://localhost/callback",
        "spiff__task_data": {"example": True},
    }

    rv = web_client().post("/v1/do/example/AsyncBodyStatus", json=payload)

    assert rv.status_code == 202
    json_resp = json.loads(rv.get_data(as_text=True))
    assert json_resp["command_response"]["http_status"] == 500
    assert json_resp["error"]["error_code"] == "AsyncStartRejected"
