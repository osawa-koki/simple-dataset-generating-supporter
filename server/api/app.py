import base64
import io
import json
import re
import uuid
from PIL import Image
import boto3

bucket_name = "simple-dataset-generating-supporter-image"
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)

def ping(_event, _context):
    """意思疎通を確認するためのAPI
    """
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
            }
        ),
    }

def list(event, _):
    """キー一覧を取得する
    """

    try:
        # 受け取ったパスパラメータから必要な値を取り出す
        query_params = event['queryStringParameters']
        user_id = query_params['user_id']
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

    # S3からキー一覧を取得する
    keys = []
    for obj in bucket.objects.filter(Prefix=f'image/{user_id}/'):
        keys.append(obj.key)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'keys': keys,
        })
    }

def fetch(event, _):
    """画像を取得する
    """

    try:
        # 受け取ったクエリパラメータから必要な値を取り出す
        path_params = event['queryStringParameters']
        user_id = path_params['user_id']
        guids = path_params['guids'].split(',')
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid request body',
                'error': 'InvalidRequestError',
                'detail': str(ex),
            })
        }

    # guidが1つ以上あるかどうかを確認する
    if len(guids) == 0:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'guids must be one or more',
                'error': 'InvalidGuidsError',
                'detail': 'guids must be one or more',
            })
        }

    # guidが30個以下かどうかを確認する
    if len(guids) > 30:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'guids must be 30 or less',
                'error': 'InvalidGuidsError',
                'detail': 'guids must be 30 or less',
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

    # guidの形式が正しいかどうかを確認する
    for guid in guids:
        if not re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', guid):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Invalid guid',
                    'error': 'InvalidGuidError',
                    'detail': 'guid must be in the format of 8-4-4-4-12 hexadecimal characters',
                })
            }

    # S3から画像を取得する
    images = []
    images_failed = []
    try:
        for guid in guids:
            key = f'image/{user_id}/{guid}'
            obj = bucket.Object(key)
            body = obj.get()['Body'].read()
            images.append({
                'key': key,
                'image': base64.b64encode(body).decode('utf-8'),
            })
    except Exception as ex:
        images_failed.append(guid)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'images': images,
            'images_failed': images_failed,
        }),
    }

def post(event, _):
    """画像を受け取り、S3に保存する

    Parameters
    ----------
    event : dict
        Lambdaのイベントオブジェクト
        {
            "body": {
                "user_id": "string",
                "image": "string",
            }
        }
    _ : object
        Lambdaのコンテキストオブジェクト
    """

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

    # 受け取ったimageプロパティをBASE64デコードする
    try:
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

    # guidを生成してS3にデータを保存する
    try:
        guid = str(uuid.uuid4())
        key = f"image/{user_id}/{guid}.png"
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
