import os
import sys
import vcr

from litestar.testing import TestClient

# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.controllers.command_controller import app as command_app
from app.controllers.query_controller import app as query_app

@vcr.use_cassette('fixtures/vcr_cassettes/command_hello.yaml')
def test_command_hello() -> None:
    with TestClient(app=command_app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.content == b'Hello, Controller!'

@vcr.use_cassette('fixtures/vcr_cassettes/query_hello.yaml')
def test_query_hello() -> None:
    with TestClient(app=query_app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.content == b'Hello, Query!'
