import base64
import io
import json
import re
import uuid
from PIL import Image
import boto3

from . import var

s3 = boto3.resource('s3')

def lambda_handler(event, _):

    try:
        # 受け取ったJSON形式のデータから必要な値を取り出す
        data = json.loads(event['body'])
        user_id = data['user_id']
        encoded_data = data['image']
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid request body',
                'error': 'InvalidRequestError',
                'detail': str(ex),
            })
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(r'^[a-zA-Z0-9_-]{3,8}$', user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid user_id',
                'error': 'InvalidUserIdError',
                'detail': 'user_id must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
            })
        }

    try:
        # 受け取ったimageプロパティをBASE64デコードする
        decoded_data = base64.b64decode(encoded_data)
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid image data',
                'error': 'InvalidImageError',
                'detail': str(ex),
            })
        }

    # デコードしたデータが画像データかどうかを確認する
    try:
        image = Image.open(io.BytesIO(decoded_data))
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid image data',
                'error': 'InvalidImageError',
                'detail': str(ex),
            })
        }

    # 画像のフォーマットがpngであることを確認する
    if image.format != 'PNG':
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid image format',
                'error': 'InvalidImageFormatError',
                'detail': 'image format must be png',
            })
        }

    # 画像のサイズが128x128であることを確認する
    width, height = image.size
    if width != 128 or height != 128:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid image size', 'error': 'InvalidImageSizeError',
                'error': 'InvalidImageSizeError',
                'detail': 'image size must be 128x128',
            })
        }

    try:
        # guidを生成してS3にデータを保存する
        guid = str(uuid.uuid4())
        key = f"image/{user_id}/{guid}.png"
        bucket = s3.Bucket(var.bucket_name)
        bucket.put_object(Key=key, Body=decoded_data)
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to save data to S3',
                'error': 'S3Error',
                'detail': str(ex),
            })
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully saved data to S3',
            'error': None,
            'detail': None,
        })
    }
