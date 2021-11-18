import json

import pytest

from watermark import app


@pytest.fixture()
def api_gw_event_text():
    return {
        "body": json.dumps({
        }),
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {
            "x-s3-process": "image/resize,w_1080,h_900/watermark,type_d3F5LXplbmhlaQ,size_30,"
                            "text_44Gy44KJ44GM44GqIC0gSGlyYWdhbmEsIO2eiOudvOqwgOuCmCDlpKnnqbrkuYvln44=,"
                            "color_222222,shadow_50,t_70,g_se,x_10,y_10,rotate_30", },
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "linyesh-mihoyo-origin-image.s3.ap-southeast-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/origin.jpg",
    }


@pytest.fixture()
def api_gw_event_image():
    return {
        "body": json.dumps({
            "origin-bucket": "linyesh-mihoyo-origin-image",
            "origin-key": "origin.jpg",
            "target-bucket": "linyesh-mihoyo-origin-image",
            "target-key": "origin.jpg",
            "x-s3-process": "image/resize,w_300,h_300/watermark,"
                            "image_bGlueWVzaC1taWhveW8tb3JpZ2luLWltYWdlL2RvLW5vdC1jb3B5LWcwOGM2MzViNDRfNjQwLnBuZw==,"
                            "color_FFFFFF,shadow_50,t_100,g_se,x_10,y_10",
        }),
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "linyesh-mihoyo-origin-image.s3.ap-southeast-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/watermark"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/watermark",
    }


@pytest.fixture()
def s3_created_put_event():
    return {
        "Records": [
            {
                "eventVersion": "2.2",
                "eventSource": "aws:s3",
                "awsRegion": "ap-southeast-1",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "eventName": "event-type",
                "userIdentity": {
                    "principalId": "Amazon-customer-ID-of-the-user-who-caused-the-event"
                },
                "requestParameters": {
                    "sourceIPAddress": "ip-address-where-request-came-from"
                },
                "responseElements": {
                    "x-amz-request-id": "Amazon S3 generated request ID",
                    "x-amz-id-2": "Amazon S3 host that processed the request"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "ID found in the bucket notification configuration",
                    "bucket": {
                        "name": "linyesh-mihoyo-origin-image",
                        "ownerIdentity": {
                            "principalId": "Amazon-customer-ID-of-the-bucket-owner"
                        },
                        "arn": "bucket-ARN"
                    },
                    "object": {
                        "key": "origin.jpg",
                        "size": "object-size in bytes",
                        "eTag": "object eTag",
                        "versionId": "object version if bucket is versioning-enabled, otherwise null",
                        "sequencer": "a string representation of a hexadecimal value used to determine event sequence, only used with PUTs and DELETEs"
                    }
                },
                "glacierEventData": {
                    "restoreEventData": {
                        "lifecycleRestorationExpiryTime": "The time, in ISO-8601 format, for example, 1970-01-01T00:00:00.000Z, of Restore Expiry",
                        "lifecycleRestoreStorageClass": "Source storage class for restore"
                    }
                }
            }
        ]
    }


def test_text_lambda_handler(api_gw_event_text):
    ret = app.lambda_handler(api_gw_event_text, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "OK"
    # assert "location" in data.dict_keys()


def test_img_lambda_handler(api_gw_event_image):
    ret = app.lambda_handler(api_gw_event_image, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "OK"
    # assert "location" in data.dict_keys()
