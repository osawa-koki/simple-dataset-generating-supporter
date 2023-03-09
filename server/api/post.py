import base64
import io
import json
from PIL import Image
import boto3
import os

bucket_name = os.environ.get('BUCKET_NAME')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    try:
        # 受け取ったJSON形式のデータから必要な値を取り出す
        data = json.loads(event['body'])
        object_key = data['key']
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

    # 画像のサイズが128x128であることを確認する
    width, height = image.size
    if width != 128 or height != 128:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid image size', 'error': 'InvalidImageSizeError'})
        }

    try:
        # S3にデータを保存する
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(Key=object_key, Body=decoded_data)
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
