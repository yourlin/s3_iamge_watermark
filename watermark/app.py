import json
import math
import os
import time
from base64 import b64decode
from enum import Enum
from mimetypes import guess_type
from urllib import parse

import boto3
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor

# Tips: 使用pillow-simd替代pillow可以获得更好的性能
# https://python-pillow.org/pillow-perf/
# CC="cc -mavx2" pip install -U --force-reinstall pillow-simd


s3 = boto3.client('s3')
img_path = '/tmp/origin/'
save_path = '/tmp/result/'


def initial():
    if not os.path.exists(img_path):
        os.mkdir(img_path)

    if not os.path.exists(save_path):
        os.mkdir(save_path)


class Position(Enum):
    NORTH_WEST = 1
    NORTH_EAST = 2
    SOUTH_WEST = 3
    SOUTH_EAST = 4
    NORTH = 5
    SOUTH = 6
    WEST = 7
    EAST = 8
    CENTER = 9


def get_relative_position(img_size, wm_size=(0, 0), position=Position.SOUTH_EAST, relative_x=0, relative_y=0):
    """
    获取相对位置
    :param img_size: 图片大小
    :param wm_size: 水印大小
    :param position: 位置
    :param relative_x: 相对偏移量x
    :param relative_y: 相对偏移量y
    :return:
    """
    # 默认左上角
    x = relative_x
    y = relative_y

    if position == Position.NORTH_EAST:
        x = img_size[0] - relative_x - wm_size[0]

    if position == Position.SOUTH_WEST:
        y = img_size[1] - relative_y - wm_size[1]

    if position == Position.SOUTH_EAST:
        x = img_size[0] - relative_x - wm_size[0]
        y = img_size[1] - relative_y - wm_size[1]

    if position == Position.EAST:
        x = img_size[0] - relative_x - wm_size[0]
        y = img_size[1] / 2.0 - relative_y - wm_size[1] / 2.0

    if position == Position.WEST:
        y = img_size[1] / 2.0 + relative_y - wm_size[1] / 2.0

    if position == Position.SOUTH:
        x = img_size[0] / 2.0 - relative_x - wm_size[0] / 2.0
        y = img_size[1] - relative_y - wm_size[1]

    if position == Position.NORTH:
        x = img_size[0] / 2.0 - relative_x - wm_size[0] / 2.0

    return x, y


# TODO：图片水印透明度
def image_watermark(img, wm_file, wm_bucket, wm_object_key,
                    position=Position.SOUTH_EAST, relative_x=0, relative_y=0,
                    shadow_radius=0, shadow_x=10, shadow_y=10):
    """
    图片水印
    @param img: 原图文件路径
    @param wm_file: 水印图文件路径
    @param wm_bucket: 水印图所在的S3 bucket的名字
    @param wm_object_key: 水印图所在的S3 bucket中的key
    @param position: 位置
    @param relative_x: 图片相对x偏移量
    @param relative_y: 图片相对y偏移量
    @param shadow_radius: 阴影模糊半径, 模糊半径>0的时候启用阴影
    @param shadow_x: 阴影x偏移量
    @param shadow_y: 阴影y偏移量
    @return: 带水印的图片
    """
    try:
        if not os.path.exists(wm_file):
            s3.download_file(wm_bucket, wm_object_key, wm_file)

        img_size = img.size
        with Image.open(wm_file) as watermark:  # 打开水印
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
        # 删除临时文件
        # os.remove(my_wm_file)
        return result_img
    except Exception as e:
        raise e


def text_watermark(img, text,
                   font,
                   text_color,
                   position=Position.SOUTH_EAST, x=10, y=10,
                   shadow_radius=0, shadow_x=10, shadow_y=10,
                   rotate_angle=0):
    """
    文字水印
    @param img: 图片路径
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
    @return: 带水印的图片
    """
    try:
        wm_size = font.getsize(text)
        watermark = Image.new('RGBA', wm_size, (255, 255, 255, 0))
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
        return result_img
    except Exception as e:
        raise e


def image_resize_handler(img, options=None, keep_ratio=True):
    """
    缩放图片大小
    @param img: 图片
    @param options:
    @param keep_ratio: 保持缩放比例
    @return: 缩放后的图片
    """
    default_options = {
        'w': 0,
        'h': 0
    }

    options = {**default_options, **options}
    new_width = int(options['w'])
    new_height = int(options['h'])
    if keep_ratio:
        image_size = img.size
        ratio = image_size[0] / image_size[1]
        if new_width / ratio > new_height:
            new_height = math.floor(new_width / ratio)
        else:
            new_width = math.floor(new_height * ratio)

    return img.resize((new_width, new_height), resample=Image.BILINEAR)


# 执行初始化
initial()


def get_font_path(font_name):
    """
    获取字体路径
    @param font_name: 字体名
    @return:
    """
    file_path = 'fonts/wqy-zenhei.ttc'
    if os.path.exists(file_path):
        return file_path
    elif os.path.exists(os.path.join('../../watermark/', file_path)):
        return os.path.join('../../watermark/', file_path)
    else:
        return None


def get_position_mapping(position_text):
    """
    解析位置参数
    @param position_text: nw：左上 north：中上 ne：右上 west：左中 center：中部 east：右中 sw：左下 south：中下 se：右下
    @return:
    """
    position = Position.SOUTH_EAST
    if position_text == 'nw':  # 左上
        position = Position.NORTH_WEST
    elif position_text == 'north':  # 上中
        position = Position.NORTH
    elif position_text == 'ne':  # 右上
        position = Position.NORTH_EAST
    elif position_text == 'west':  # 左中
        position = Position.WEST
    elif position_text == 'center':  # 中部
        position = Position.CENTER
    elif position_text == 'east':  # 右中
        position = Position.EAST
    elif position_text == 'sw':  # 左下
        position = Position.SOUTH_WEST
    elif position_text == 'south':  # 中下
        position = Position.SOUTH
    elif position_text == 'se':  # 右下
        position = Position.SOUTH_EAST

    return position


# todo: gif添加水印
def watermark_handler(img, options=None):
    """
    水印处理
    @param img_file: 图片
    @param options: 参数组
    @return:
    """
    default_options = {'type': 'wqy-zenhei',  # 字体 TODO:暂时不支持字体选择
                       'size': 40,  # 指定文字水印的文字大小。
                       'text': '',  # 文本内容
                       'color': 'FFFFFF',  # 字体颜色
                       'shadow': 0,  # 指定文字水印的阴影透明度。
                       'shadow_radius': 5,  # 模糊半径
                       'shadow_x': 10,  # 阴影偏移量x
                       'shadow_y': 10,  # 阴影偏移量y
                       't': 0,  # 指定图片水印或水印文字的透明度。
                       'g': 'se',  # 指定水印在图片中的位置。nw：左上 north：中上 ne：右上 west：左中 center：中部 east：右中 sw：左下 south：中下 se：右下
                       'x': 0,  # x相对偏移量
                       'y': 0,  # y相对偏移量
                       'rotate': 0,  # 指定文字顺时针旋转角度。
                       'image': None  # bucket/object_key, 例如 linyesh-mihoyo-origin-image/do-not-copy-g08c635b44_640.png
                       }
    options = {**default_options, **options}
    print('合并：' + json.dumps(options))
    try:
        position = get_position_mapping(options['g'])
        if options['image'] is None:
            print('开始处理文本水印')
            font_path = get_font_path(options['type'])
            font_size = int(options['size'])
            font = ImageFont.truetype(font_path, font_size)
            if font is None:
                raise Exception("未找到字体文件")
            alpha = int(float(options['t']) / 100.0 * 255)
            text_color = ImageColor.getcolor('#' + options['color'], "RGB") + (alpha,)
            result_img = text_watermark(img,
                                        b64decode(options['text']).decode('utf-8'),
                                        font=font,
                                        text_color=text_color,
                                        position=position,
                                        x=int(options['x']),
                                        y=int(options['y']),
                                        shadow_radius=int(options['shadow_radius']),
                                        shadow_x=int(options['shadow_x']),
                                        shadow_y=int(options['shadow_y']),
                                        rotate_angle=int(options['rotate']))
        else:
            print('开始处理图片水印')
            my_wm_file = os.path.join('/tmp/wm', time.time(), '.jpg')
            img_sp = options['image'].split('/')
            wm_bucket = img_sp[0]
            wm_object_key = '/'.join(img_sp[1:])
            result_img = image_watermark(img,
                                         wm_file=my_wm_file,
                                         wm_bucket=wm_bucket,
                                         wm_object_key=wm_object_key,
                                         position=position,
                                         relative_x=options['x'],
                                         relative_y=options['y'],
                                         shadow_radius=options['shadow_radius'],
                                         shadow_x=options['shadow_x'],
                                         shadow_y=options['shadow_y'],
                                         )
        return result_img
    except Exception as e:
        raise e


def lambda_handler(event, context):
    # https://linyesh-mihoyo-origin-image.s3.ap-southeast-1.amazonaws.com/origin.jpg?x-oss-process=image
    # /resize,w_300,h_300
    # /watermark,type_d3F5LXplbmhlaQ,size_30,text_SGVsbG8gV29ybGQ,color_FFFFFF,shadow_50,t_100,g_se,x_10,y_10
    method = event['httpMethod']
    parameters = []
    body = json.loads(event['body'])
    headers = event['headers']
    # img_bucket = headers['Host'].split('.')[0]
    # img_key = event['path'].strip('/')
    img_bucket = body['origin-bucket']
    img_key = body['origin-key']
    if 'target-bucket' not in body:
        target_bucket = img_bucket
    else:
        target_bucket = body['target-bucket']
    if 'target-key' not in body:
        target_key = img_key
    else:
        target_key = body['target-key']
    # if method == 'POST':
    parameters = event['queryStringParameters']['x-s3-process'].split('/')
    # print("parameters: %s" % parameters)

    img_file = os.path.join(img_path, img_key)
    process_target = parameters[0]
    if process_target != 'image':
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": 'invalid parameters',
            }),
        }

    # 从S3下载原图在本地进行处理
    t1 = time.time()
    s3.download_file(img_bucket, img_key, img_file)
    print('下载原图耗时%.3fs' % (time.time() - t1))
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
    # 图像处理
    with Image.open(img_file) as result_img:  # 打开图片
        quality = 100
        for parameter in parameters[1:]:
            op_list = parameter.split(',')
            op = op_list[0]
            op_parameter_dict = {}
            for op_parameter in op_list[1:]:
                kp = op_parameter.split('_')
                op_parameter_dict[kp[0]] = kp[1]

            if op == 'watermark':
                t1 = time.time()
                result_img = watermark_handler(result_img, options=op_parameter_dict)
                print('水印处理耗时%.3fs' % (time.time() - t1))
            elif op == 'resize':
                t1 = time.time()
                result_img = image_resize_handler(result_img, options=op_parameter_dict)
                print('图片缩放处理耗时%.3fs' % (time.time() - t1))
            elif op == 'quality':
                if 'q' in op_parameter_dict:
                    quality = 100 * op_parameter_dict['q']
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "message": 'invalid parameters',
                    }),
                }
        # 图片上传
        if result_img is not None:
            # result_img.show()
            new_file_name = os.path.join(save_path, img_file.split('/')[-1])
            result_img.save(new_file_name, quality=quality)
            file_mine = guess_type(new_file_name)
            tags = {"updated": "1", 'watermark': '1'}
            s3.upload_file(new_file_name,
                           target_bucket,
                           target_key,
                           ExtraArgs={
                               "Tagging": parse.urlencode(tags),
                               'ContentType': file_mine[0]
                           })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "OK"
        }),
    }
