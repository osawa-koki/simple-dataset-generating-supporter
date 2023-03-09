import base64
import io
import json
from PIL import Image
import boto3
import os

bucket_name = os.environ.get('BUCKET_NAME')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    # 受け取ったJSON形式のデータから必要な値を取り出す
    data = json.loads(event['body'])
    object_key = data['key']
    encoded_data = data['image']

    # 受け取ったimageプロパティをBASE64デコードする
    decoded_data = base64.b64decode(encoded_data)

    # デコードしたデータが画像データかどうかを確認する
    try:
        image = Image.open(io.BytesIO(decoded_data))
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid image data', 'error': 'InvalidImageError'})
        }

    # 画像のサイズが128x128であることを確認する
    width, height = image.size
    if width != 128 or height != 128:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid image size', 'error': 'InvalidImageSizeError'})
        }

    # S3にデータを保存する
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(Key=object_key, Body=decoded_data)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully saved data to S3',
            'error': None,
        })
    }
