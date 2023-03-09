import json
import os
import pytest
from unittest.mock import patch, MagicMock
from moto import mock_s3
from ...api import app

# ユーザ名とカテゴリは3文字以上8文字以下で、半角英数字、ハイフン、アンダースコアのみを許可する
@pytest.mark.parametrize(
    "user_id, category, is_valid", [
        ("user", "category", True),
        ("---", "___", True),
        ("___", "---", True),
        ("aaaaaaaa", "aaaaaaaa", True),
        ("user", "category_xxxxx", False),
        ("user_xxxxx", "category", False),
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
        ret = app.post(event, "")
        if is_valid:
            assert ret["statusCode"] == 200
        else:
            assert ret["statusCode"] == 400
