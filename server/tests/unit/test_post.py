import json
import os
import pytest
from unittest.mock import MagicMock, patch
from moto import mock_s3
import boto3
from ...api import post
from ...api import var

# ユーザ名は3文字以上8文字以下で、半角英数字、ハイフン、アンダースコアのみを許可する
@pytest.mark.parametrize(
    "user_id, is_valid", [
        ("", False),
        ("a", False),
        ("aa", False),
        ("aaa", True),
        ("aaaa", True),
        ("aAa", True),
        ("a-a", True),
        ("a_a", True),
        ("a a", False),
        ("aあa", False),
        ("aaaaaaaaa", False),
    ]
)
@mock_s3
def test_lambda_handler_params(user_id, is_valid):
    # S3 クライアントのモックを作成
    mock_s3_client = boto3.resource('s3')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "valid_image.txt")
    with open(file_path, "r") as f:
        image = f.read()

    # リクエストボディを作成する
    body = {
        "user_id": user_id,
        "image": image,
    }
    event = {
        "body": json.dumps(body),
    }

    # リクエストボディの内容に応じて、正しいレスポンスが返ってくることを確認する
    with patch.object(mock_s3_client.Bucket(var.bucket_name), 'put_object', MagicMock()):
        ret = post.lambda_handler(event, "")
        if is_valid:
            assert ret["statusCode"] == 200
        else:
            assert ret["statusCode"] == 400
