import base64
import io
import json
import re
import tempfile
import uuid
import zipfile
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
USER_ID_REGEX = r'^[a-zA-Z0-9_-]{3,16}$'
USER_ID_INVALID_MESSAGE = 'user_id must be 3 or more characters, 16 or less characters, and only contain alphanumeric characters, hyphens, and underscores'
CATEGORY_REGEX = r'^[a-zA-Z0-9_-]{1,8}$'
CATEGORY_INVALID_MESSAGE = 'category must be 1 or more characters, 8 or less characters, and only contain alphanumeric characters, hyphens, and underscores'
GUID_REGEX = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
GUID_INVALID_MESSAGE = 'guid must be UUID format'
HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

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
                'message': str(ex),
            }),
            'headers': HEADERS,
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': USER_ID_INVALID_MESSAGE,
            }),
            'headers': HEADERS,
        }

    # S3からキー一覧を取得する
    keys = []
    for obj in bucket.objects.filter(Prefix=f'image/{user_id}/'):
        keys.append(obj.key)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'keys': keys,
        }),
        'headers': HEADERS,
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
                'message': str(ex),
            }),
            'headers': HEADERS,
        }

    # guidが1つ以上あるかどうかを確認する
    if len(guids) == 0:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'guids must be 1 or more',
            }),
            'headers': HEADERS,
        }

    # guidが300個以下かどうかを確認する
    if len(guids) > 300:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'guids must be 30 or less',
            }),
            'headers': HEADERS,
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': USER_ID_INVALID_MESSAGE,
            }),
            'headers': HEADERS,
        }

    # categoryの形式が正しいかどうかを確認する
    if not re.match(CATEGORY_REGEX, category):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': CATEGORY_INVALID_MESSAGE,
            }),
            'headers': HEADERS,
        }

    # guidの形式が正しいかどうかを確認する
    for guid in guids:
        if not re.match(GUID_REGEX, guid):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': GUID_INVALID_MESSAGE,
                }),
            'headers': HEADERS,
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
        'headers': HEADERS,
    }

def upload(event, _):
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
                'message': str(ex),
            }),
            'headers': HEADERS,
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': USER_ID_INVALID_MESSAGE
            }),
            'headers': HEADERS,
        }

    # categoryの形式が正しいかどうかを確認する
    if not re.match(CATEGORY_REGEX, category):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': CATEGORY_INVALID_MESSAGE
            }),
            'headers': HEADERS,
        }

    # 受け取ったimageプロパティをBASE64デコードする
    try:
        decoded_data = base64.b64decode(encoded_data)
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid image data',
            }),
            'headers': HEADERS,
        }

    # デコードしたデータが画像データかどうかを確認する
    try:
        image = Image.open(io.BytesIO(decoded_data))
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid image data',
            }),
            'headers': HEADERS,
        }

    # 画像のフォーマットがpngであることを確認する
    if image.format != IMAGE_FORMAT:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid image format',
            }),
            'headers': HEADERS,
        }

    # 画像のサイズを128x128にリサイズする
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE))

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
            }),
            'headers': HEADERS,
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully saved data to S3',
        }),
        'headers': HEADERS,
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
                'message': str(ex),
            }),
            'headers': HEADERS,
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': USER_ID_INVALID_MESSAGE
            }),
            'headers': HEADERS,
        }

    # categoryの形式が正しいかどうかを確認する
    if not re.match(CATEGORY_REGEX, category):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': CATEGORY_INVALID_MESSAGE
            }),
            'headers': HEADERS,
        }

    # guidの形式が正しいかどうかを確認する
    if not re.match(GUID_REGEX, guid):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': GUID_INVALID_MESSAGE
            }),
            'headers': HEADERS,
        }

    # S3から画像を削除する
    try:
        key = f"image/{user_id}/{category}/{guid}.png"
        s3.Object(bucket_name, key).delete()
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to delete data from S3',
            }),
            'headers': HEADERS,
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully deleted data from S3',
        }),
        'headers': HEADERS,
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
                'message': str(ex),
            }),
            'headers': HEADERS,
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': USER_ID_INVALID_MESSAGE,
            }),
            'headers': HEADERS,
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
            }),
            'headers': HEADERS,
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully deleted data from S3',
        }),
        'headers': HEADERS,
    }

def download(event, _):
    """画像を一括でダウンロードする
    """

    try:
        # 受け取ったクエリパラメータから必要な値を取り出す
        path_params = event[QUERY_STRING_PARAMETERS]
        user_id = path_params[USER_ID]
        category = path_params[CATEGORY]
    except Exception as ex:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': str(ex),
            }),
            'headers': HEADERS,
        }

    # user_idの形式が正しいかどうかを確認する
    if not re.match(USER_ID_REGEX, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': USER_ID_INVALID_MESSAGE,
            }),
            'headers': HEADERS,
        }

    # categoryの形式が正しいかどうかを確認する
    if not re.match(CATEGORY_REGEX, category):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': CATEGORY_INVALID_MESSAGE,
            }),
            'headers': HEADERS,
        }

    # S3から画像を取得する
    images = []
    images_failed = []
    try:
        key = f"image/{user_id}/{category}/"
        for obj in bucket.objects.filter(Prefix=key):
            # オブジェクトを取得する
            image_data = obj.get()['Body'].read()
            guid = obj.key.split('/')[-1]
            # 配列に格納する
            image_object = {
                'path': guid,
                'image': image_data,
            }
            images.append(image_object)
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to get data from S3',
            }),
            'headers': HEADERS,
        }

    # ファイルをZIP化する
    guid = str(uuid.uuid4())
    zip_path = f"/tmp/{guid}.zip"
    # 一時ディレクトリを作成する
    with tempfile.TemporaryDirectory() as temp_dir:
        # 各ファイルを一時ディレクトリに書き込む
        for image_object in images:
            file_path = temp_dir + image_object["path"]
            with open(file_path, "wb") as f:
                f.write(image_object["image"])
        # 一時ディレクトリ内のファイルをZIPファイルに追加する
        with zipfile.ZipFile(zip_path, "w") as zip:
            for image_object in images:
                file_path = temp_dir + image_object["path"]
                zip.write(file_path, arcname=image_object["path"])

    # ZIPファイルをBASE64エンコードする
    with open(zip_path, "rb") as f:
        zip_data = f.read()
        zip_data_base64 = base64.b64encode(zip_data).decode("utf-8")

    return {
        'statusCode': 200,
        'body': zip_data_base64,
        'headers': {
            'Content-Type': 'application/zip',
        },
        'isBase64Encoded': True,
    }
