import json

def ping(event, context):
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
