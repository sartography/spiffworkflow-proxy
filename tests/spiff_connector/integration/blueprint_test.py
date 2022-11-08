from flask import Flask
from spiff_connector.spiff_connector_blueprint import spiff_connector_blueprint

def test_blueprint():
    app = Flask(__name__)
    app.register_blueprint(spiff_connector_blueprint)

    web = app.test_client()

    rv = web.get("/")
    assert rv.status == '200 OK'