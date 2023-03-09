import json
from ...api import ping

def test_lambda_handler():

    ret = ping.lambda_handler({}, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "hello world"
