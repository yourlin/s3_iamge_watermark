import json
import os
from enum import Enum
from urllib import parse
import boto3
from PIL import Image, ImageDraw, ImageFont

s3 = boto3.client('s3')
wm_bucket = 'linyesh-mihoyo-origin-image'
wm_key = 'do-not-copy-g08c635b44_640.png'
my_wm_file = '/tmp/wm.jpg'
img_path = '/tmp/origin/'
save_path = '/tmp/result/'


def initial():
    if not os.path.exists(img_path):
        os.mkdir(img_path)

    if not os.path.exists(save_path):
        os.mkdir(save_path)


class Position(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


def get_relative_position(img_size, wm_size=(0, 0), position=Position.BOTTOM_RIGHT, relative_x=0, relative_y=0):
    """
    获取相对位置
    :param img_size: 图片大小
    :param wm_size: 水印大小
    :param position: 位置
    :param relative_x: 相对偏移量x
    :param relative_y: 相对偏移量y
    :return:
    """
    x = relative_x
    y = relative_y

    if position == Position.TOP_RIGHT:
        x = img_size[0] - relative_x - wm_size[0]

    if position == Position.BOTTOM_LEFT:
        y = img_size[1] - relative_y - wm_size[1]

    if position == Position.BOTTOM_RIGHT:
        x = img_size[0] - relative_x - wm_size[0]
        y = img_size[1] - relative_y - wm_size[1]

    return x, y


def image_watermark(img_file, wm_file, position=Position.BOTTOM_RIGHT, relative_x=0, relative_y=0):
    try:
        if not os.path.exists(wm_file):
            s3.download_file(wm_bucket, wm_key, wm_file)

        img = Image.open(img_file)  # 打开图片
        img_size = img.size
        watermark = Image.open(wm_file)  # 打开水印
        wm_size = watermark.size
        # 如果图片大小小于水印大小
        if img_size[0] < wm_size[0]:
            watermark.resize(tuple(map(lambda x: int(x * 0.5), watermark.size)))
        # 新建一个图层
        layer = Image.new('RGBA', img.size)
        # 将水印图片添加到图层上
        layer.paste(watermark, get_relative_position(img_size, wm_size, position, relative_x, relative_y))
        mark_img = Image.composite(layer, img, layer)
        new_file_name = os.path.join(save_path, img_file.split('/')[-1])
        mark_img.save(new_file_name)

        return new_file_name
    except Exception as e:
        raise e


def text_watermark(img_file, text,
                   font=ImageFont.truetype('../../watermark/fonts/wqy-zenhei.ttc', 60),
                   text_color=(50, 50, 50, 255),
                   position=Position.BOTTOM_RIGHT,
                   x=10,
                   y=10):
    try:
        img = Image.open(img_file)  # 打开图片
        draw = ImageDraw.Draw(img)
        relative_position = get_relative_position(img.size,
                                                  wm_size=draw.textsize(text, font=font),
                                                  position=position,
                                                  relative_x=x,
                                                  relative_y=y)
        draw.text(relative_position, text, font=font, fill=text_color)
        new_file_name = os.path.join(save_path, img_file.split('/')[-1])
        img.save(new_file_name)
        img.show()

        return new_file_name
    except Exception as e:
        raise e


# 执行初始化
initial()


def lambda_handler(event, context):
    body = json.loads(event['body'])
    img_bucket = body['origin-bucket']
    img_key = body['origin-key']
    target_bucket = body['target-bucket']
    target_key = body['target-key']
    img_file = os.path.join(img_path, img_key)

    # 图片已经处理过，则不操作
    response = s3.get_object_tagging(
        Bucket=img_bucket,
        Key=img_key)
    is_updated = False
    for tag in response['TagSet']:
        if tag['Key'] == 'updated' and tag['Value'] == '1':
            is_updated = True
            break
    if is_updated:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": 'OK',
            }),
        }

    # 从S3下载原图在本地进行处理
    s3.download_file(img_bucket, img_key, img_file)
    try:
        new_file_name = text_watermark(img_file, 'ひらがな - Hiragana, 히라가나 天空之城', position=Position.TOP_LEFT)
        # new_file_name = image_watermark(img_file, my_wm_file, Position.BOTTOM_RIGHT, 20, 20)
        # tags = {"updated": "1", 'watermark': '1'}
        # s3.upload_file(new_file_name,
        #                target_bucket,
        #                target_key,
        #                ExtraArgs={"Tagging": parse.urlencode(tags)}
        #                )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": e,
            }),
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "OK"
        }),
    }
