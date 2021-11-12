import json
import boto3
import requests

s3 = boto3.client('s3')
api_url = 'https://demo.mihoyo.com'


def lambda_handler(event, context):
    body = json.loads(event['body'])
    img_bucket = body['origin-bucket']
    img_key = body['origin-key']

    # 图片已经处理过，则不操作
    response = s3.get_object_tagging(
        Bucket=img_bucket,
        Key=img_key)
    is_updated = False
    for tag in response['TagSet']:
        if tag['tag'] == 'updated' and tag['value'] == '1':
            is_updated = True
            break
    if not is_updated:
        requests.get(api_url, {
            'bucket': 1,
            'key': '2'
        })
