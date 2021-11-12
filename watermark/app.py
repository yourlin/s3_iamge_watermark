import json
import os
from enum import Enum

import boto3
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
    FILL = 5


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


def image_watermark(img_file, wm_file,
                    position=Position.BOTTOM_RIGHT, relative_x=0, relative_y=0,
                    shadow_radius=0, shadow_x=10, shadow_y=10):
    """
    图片水印
    @param img_file: 原图文件路径
    @param wm_file: 水印图文件路径
    @param position: 位置
    @param relative_x: 图片相对x偏移量
    @param relative_y: 图片相对y偏移量
    @param shadow_radius: 阴影模糊半径, 模糊半径>0的时候启用阴影
    @param shadow_x: 阴影x偏移量
    @param shadow_y: 阴影y偏移量
    @return:
    """
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
        # 新建水印图层
        wm_layer = Image.new('RGBA', img_size)

        # 将水印图片添加到图层
        wm_position = get_relative_position(img_size, wm_size, position, relative_x, relative_y)
        wm_layer.paste(watermark, wm_position)

        if shadow_radius > 0:
            layer_shadow = Image.new('RGBA', img_size)
            wm_shadow_position = (wm_position[0] + shadow_x, wm_position[1] + shadow_y)
            layer_shadow.paste(watermark, wm_shadow_position)
            layer_shadow = layer_shadow.filter(ImageFilter.GaussianBlur(radius=shadow_radius))
            img = Image.composite(layer_shadow, img, layer_shadow)
        result_img = Image.composite(wm_layer, img, wm_layer)
        new_file_name = os.path.join(save_path, img_file.split('/')[-1])
        result_img.save(new_file_name)
        result_img.show()

        return new_file_name
    except Exception as e:
        raise e


def text_watermark(img_file, text,
                   font=ImageFont.truetype('../../watermark/fonts/wqy-zenhei.ttc', 60),
                   text_color=(50, 50, 50, 255),
                   position=Position.BOTTOM_RIGHT, x=10, y=10,
                   shadow_radius=0, shadow_x=10, shadow_y=10,
                   rotate_angle=0):
    """
    文字水印
    @param img_file: 图片路径
    @param text: 文本信息
    @param font: 字体
    @param text_color: 文本颜色（R,G,B,A）
    @param position: 位置信息
    @param x: x偏移量
    @param y: y偏移量
    @param shadow_radius: 阴影模糊半径, 模糊半径>0的时候启用阴影
    @param shadow_x: 阴影x偏移量
    @param shadow_y: 阴影y偏移量
    @param rotate_angle: 转动角度
    @return:
    """
    try:
        img = Image.open(img_file)  # 打开图片
        wm_size = font.getsize(text)
        watermark = Image.new('RGBA', wm_size)
        wm_draw = ImageDraw.Draw(watermark)
        wm_draw.text((0, 0), text, font=font, fill=text_color)
        if rotate_angle > 0:
            watermark = watermark.rotate(rotate_angle, expand=1)
        # 新建水印图层
        wm_layer = Image.new('RGBA', img.size)
        wm_position = get_relative_position(img.size,
                                            wm_size=watermark.size,
                                            position=position,
                                            relative_x=x,
                                            relative_y=y)
        wm_layer.paste(watermark, wm_position)
        if shadow_radius > 0:
            layer_shadow = Image.new('RGBA', img.size)
            wm_shadow_position = (wm_position[0] + shadow_x, wm_position[1] + shadow_y)
            layer_shadow.paste(watermark, wm_shadow_position)
            layer_shadow = layer_shadow.filter(ImageFilter.GaussianBlur(radius=shadow_radius))
            img = Image.composite(layer_shadow, img, layer_shadow)

        result_img = Image.composite(wm_layer, img, wm_layer)
        new_file_name = os.path.join(save_path, img_file.split('/')[-1])
        result_img.save(new_file_name)
        result_img.show()

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
        new_file_name = text_watermark(img_file, 'ひらがな - Hiragana, 히라가나 天空之城', position=Position.BOTTOM_RIGHT,
                                       shadow_radius=5, shadow_x=10, shadow_y=10, rotate_angle=30)
        # new_file_name = image_watermark(img_file, my_wm_file, Position.BOTTOM_RIGHT, 20, 20, 5, 10, 10)
        # tags = {"updated": "1", 'watermark': '1'}
        # s3.upload_file(new_file_name,
        #                target_bucket,
        #                target_key,
        #                ExtraArgs={"Tagging": parse.urlencode(tags)}
        #                )
    except Exception as e:
        print(e)
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
