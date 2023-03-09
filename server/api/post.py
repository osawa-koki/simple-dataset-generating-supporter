import base64
import json
import boto3

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    # 受け取ったJSON形式のデータから必要な値を取り出す
    data = json.loads(event['body'])
    bucket_name = 'simple-dataset-generating-supporter-image'
    object_key = data['key']
    encoded_data = data['image']

    # 受け取ったimageプロパティをBASE64デコードする
    #decoded_data = base64.b64decode(encoded_data)
    decoded_data = encoded_data

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
