import base64
import io
import json
import re
import uuid
from PIL import Image
import boto3

# 固定数の定義
IMAGE_SIZE = 128
IMAGE_FORMAT = 'PNG'
QUERY_STRING_PARAMETERS = 'queryStringParameters'
USER_ID = 'user_id'
CATEGORY = 'category'
GUID = 'guid'
GUIDS = 'guids'
USER_ID_REGEX = r'^[a-zA-Z0-9_-]{3,8}$'
CATEGORY_REGEX = r'^[a-zA-Z0-9_-]{3,8}$'
GUID_REGEX = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'

# BUCKET_NAME環境変数からバケット名を取得する
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
        query_params = event[QUERY_STRING_PARAMETERS]
        user_id = query_params[USER_ID]
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
    if not re.match(USER_ID_REGEX, user_id):
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
        path_params = event[QUERY_STRING_PARAMETERS]
        user_id = path_params[USER_ID]
        category = path_params[CATEGORY]
        guids = path_params[GUIDS].split(',')
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
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid user_id',
                'error': 'InvalidUserIdError',
                'detail': 'user_id must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
            })
        }

    # categoryの形式が正しいかどうかを確認する
    if not re.match(CATEGORY_REGEX, category):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid category',
                'error': 'InvalidCategoryError',
                'detail': 'category must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
            })
        }

    # guidの形式が正しいかどうかを確認する
    for guid in guids:
        if not re.match(GUID_REGEX, guid):
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
            key = f'image/{user_id}/{category}/{guid}.png'
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
                "category": "string",
                "image": "string",
            }
        }
    _ : object
        Lambdaのコンテキストオブジェクト
    """

    try:
        # 受け取ったJSON形式のデータから必要な値を取り出す
        data = json.loads(event['body'])
        user_id = data[USER_ID]
        category = data[CATEGORY]
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
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid user_id',
                'error': 'InvalidUserIdError',
                'detail': 'user_id must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
            })
        }

    # categoryの形式が正しいかどうかを確認する
    if not re.match(CATEGORY_REGEX, category):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid category',
                'error': 'InvalidCategoryError',
                'detail': 'category must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
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
    if image.format != IMAGE_FORMAT:
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
    if width != IMAGE_SIZE or height != IMAGE_SIZE:
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
        key = f"image/{user_id}/{category}/{guid}.png"
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
        }),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent',
            'Access-Control-Allow-Methods': 'GET,OPTIONS,POST,PUT,DELETE',
            'Access-Control-Allow-Credentials': True,
        },
    }

def delete(event, _):
    """画像を削除する

    Parameters
    ----------
    event : dict
        Lambdaのイベントオブジェクト
        {
            "queryStringParameters": {
                "user_id": "string",
                "category": "string",
                "guid": "string",
            }
        }
    _ : object
        Lambdaのコンテキストオブジェクト
    """

    try:
        # クエリパラメータから必要な値を取り出す
        query_params = event[QUERY_STRING_PARAMETERS]
        user_id = query_params[USER_ID]
        category = query_params[CATEGORY]
        guid = query_params[GUID]
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid request path',
                'error': 'InvalidRequestError',
                'detail': str(ex),
            })
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid user_id',
                'error': 'InvalidUserIdError',
                'detail': 'user_id must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
            })
        }

    # categoryの形式が正しいかどうかを確認する
    if not re.match(CATEGORY_REGEX, category):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid category',
                'error': 'InvalidCategoryError',
                'detail': 'category must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
            })
        }

    # guidの形式が正しいかどうかを確認する
    if not re.match(GUID_REGEX, guid):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid guid',
                'error': 'InvalidGuidError',
                'detail': 'guid must be in the format of 8-4-4-4-12 hexadecimal characters',
            })
        }

    # S3から画像を削除する
    try:
        key = f"image/{user_id}/{category}/{guid}.png"
        s3.delete_object(Bucket=bucket_name, Key=key)
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to delete data from S3',
                'error': 'S3Error',
                'detail': str(ex),
            })
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully deleted data from S3',
            'error': None,
            'detail': None,
        })
    }

def truncate(event, _):
    """画像を全て削除する

    Parameters
    ----------
    event : dict
        Lambdaのイベントオブジェクト
        {
            "queryStringParameters": {
                "user_id": "string",
                "category": "string",
            }
        }
    _ : object
        Lambdaのコンテキストオブジェクト
    """

    try:
        # クエリパラメータから必要な値を取り出す
        query_params = event[QUERY_STRING_PARAMETERS]
        user_id = query_params[USER_ID]
        category = query_params[CATEGORY]
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid request path',
                'error': 'InvalidRequestError',
                'detail': str(ex),
            })
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid user_id',
                'error': 'InvalidUserIdError',
                'detail': 'user_id must be 3 or more characters and only contain alphanumeric characters, hyphens, and underscores',
            })
        }

    # categoryの形式が正しいかどうかを確認する

    # S3から画像を削除する
    try:
        key = f"image/{user_id}/{category}/"
        bucket.objects.filter(Prefix=key).delete()
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to delete data from S3',
                'error': 'S3Error',
                'detail': str(ex),
            })
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully deleted data from S3',
            'error': None,
            'detail': None,
        })
    }
