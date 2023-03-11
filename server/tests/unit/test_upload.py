import json
import os
import pytest
from unittest.mock import patch, MagicMock
from moto import mock_s3
from ...api import app

# USER_ID_REGEX = r'^[a-zA-Z0-9_-]{3,16}$'
# CATEGORY_REGEX = r'^[a-zA-Z0-9_-]{1,8}$'
@pytest.mark.parametrize(
    "user_id, category, is_valid", [
        ("user", "category", True),
        ("", "category", False),
        ("user", "", False),
        ("x x", "category", False),
        ("user", "x x", False),
    ]
)
@mock_s3
def test_lambda_handler_params(user_id, category, is_valid):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "valid_image.txt")
    with open(file_path, "r") as f:
        image = f.read()

    # リクエストボディを作成する
    body = {
        "user_id": user_id,
        "category": category,
        "image": image,
    }
    event = {
        "body": json.dumps(body),
    }

    # S3リソースをモック化する
    with patch.object(app.bucket, 'put_object') as mock_put_object:
        # モック化したS3リソースのオブジェクトを返すようにする
        mock_put_object.return_value = MagicMock()
        # リクエストボディの内容に応じて、正しいレスポンスが返ってくることを確認する
        ret = app.upload(event, "")
        if is_valid:
            assert ret["statusCode"] == 200
        else:
            assert ret["statusCode"] == 400
