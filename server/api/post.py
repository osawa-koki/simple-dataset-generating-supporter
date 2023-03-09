import base64
import boto3

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    bucket_name = 'simple-dataset-generating-supporter-image'
    object_key = event['key']

    # 受け取ったimageプロパティをBASE64デコードする
    encoded_data = event['image']
    # decoded_data = base64.b64decode(encoded_data)
    decoded_data = encoded_data

    # S3にデータを保存する
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(Key=object_key, Body=decoded_data)

    return {
        'statusCode': 200,
        'body': 'Successfully saved data to S3'
    }
