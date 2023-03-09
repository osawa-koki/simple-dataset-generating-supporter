import json

import pytest

from api import app

def test_lambda_handler(apigw_event, mocker):

    ret = app.ping({}, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "hello world"
