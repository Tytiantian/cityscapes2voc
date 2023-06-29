import json
import base64
import os
from PIL import Image


# 读取图片文件并生成imgdata
def generate_imgdata(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
        imgdata = base64.b64encode(image_data).decode('utf-8')
    return imgdata


# 读取JSON文件
def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


# 写入JSON文件
def write_json(data, file_path, ini_json_data, img_data, img_path):
    with open(file_path, 'w') as f:
        result_dict = {'verson': '3.16.7', 'flags': {}, 'shapes': data, 'lineColor': [0, 255, 0, 128],
                       'fillColor': [255, 0, 0, 128], 'imagePath': img_path, 'imageData': img_data,
                       'imageHeight': ini_json_data['imgHeight'], 'imageWidth': ini_json_data['imgWidth']}
        json.dump(result_dict, f, indent=4)


# 提取符合条件的数据
def extract_data(json_data_f, label):
    extra_data = []
    object_data = json_data_f['objects']

    # 不能改变各个points的存放顺序，否则生成的png会有错误
    for item in object_data:
        if item['label'] in label:
            new_dict = {'label': item['label'], 'line_color': None, 'fill_color': None,
                        'points': item['polygon'], 'shape_type': 'polygon', 'flags': {}}
            extra_data.append(new_dict)
        else:
            new_dict = {'label': '_background_', 'line_color': None, 'fill_color': None,
                        'points': item['polygon'], 'shape_type': 'polygon', 'flags': {}}
            extra_data.append(new_dict)

    return extra_data


if __name__ == '__main__':
    # 要转换的数据集和需要的标签
    target_label = ['sky', 'person', 'vegetation', 'terrain', 'car', 'building', 'ground', 'road']  # 填写需要的类别

    # 指定输入数据路径
    path_gtFine = './gtFine/train/'   # 标签数据文件夹  这里使用train里面的两个城市各4张图片作为示例
    path_leftImg8bit = './leftImg8bit/train/'   # 原图像文件夹   同样是train里面的两个城市各4张图片作为示例

    # 指定输出数据路径，将png图片转为jpg存储在一个文件夹,这里会存储转换好的json和jpg
    output_file_path = './before/'

    # 获取城市文件夹列表
    folders = [f for f in os.listdir(path_gtFine) if os.path.isdir(os.path.join(path_gtFine, f))]

    for i, city in enumerate(folders):
        print("\n共{}个城市，目前是第{}个：{}".format(len(folders), i+1, city))
        city_path = path_leftImg8bit + '/' + city
        for j, file_name in enumerate(os.listdir(path_leftImg8bit + '/' + city)):
            print("\r" + city + " Progress: {}/{}".format(j+1, len(os.listdir(path_leftImg8bit + '/' + city))), end='')

            result = file_name.replace("leftImg8bit.png", "gtFine_polygons.json")

            file_path_png = os.path.join(path_leftImg8bit + '/' + city, file_name)
            file_path_json = os.path.join(path_gtFine + '/' + city, result)

            # 获取lableme的imgdata
            imgdata = generate_imgdata(file_path_png)

            # 读取JSON文件
            json_data = read_json(file_path_json)

            # 提取符合条件的数据
            extracted_data = extract_data(json_data, target_label)

            # 写入新的JSON文件
            img_path_ = file_name.replace(".png", ".jpg")
            write_json(extracted_data, output_file_path + file_name.replace(".png", ".json"), json_data, imgdata, img_path_)

            # 转换png为jpg并写入图片数据
            png_image = Image.open(file_path_png)
            png_image.convert("RGB").save(output_file_path + img_path_, "JPEG")
