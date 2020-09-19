# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError

import os
import sys
import logging
import shutil

# 腾讯云COSV5Python SDK, 目前可以支持Python2.6与Python2.7以及Python3.x
# pip安装指南:pip install -U cos-python-sdk-v5
# cos最新可用地域,参照https://www.qcloud.com/document/product/436/6224

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 设置用户属性, 包括secret_id, secret_key, region
# appid已在配置中移除,请在参数Bucket中带上appid。Bucket由bucketname-appid组成
secret_id = 'AKIDEIBrJX2KtELFvOneXCcnmW2KNDpCuHyR'     # 替换为用户的secret_id
secret_key = 'MVR8bqsgFahaFfrpZ5NQGrDLGwObaLr9'     # 替换为用户的secret_key
region = 'ap-chengdu'    # 替换为用户的region
token = None               # 使用临时密钥需要传入Token，默认为空,可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)  # 获取配置对象
client = CosS3Client(config)
print("已连接腾讯COS")


galleries = []
json_name = "galleries.yaml"    # 图片数据文件名称
bucket_name = "hexo-1257031621"      # 腾讯COS存储桶名称
photos_name = "galleries/"      # 腾讯COS一级相册目录

# json文件保存路径 例：D://blog/source/_data/galleries.json
cwd = os.getcwd().replace("photos", "_data")
json_cwd = os.path.join(cwd, json_name).replace('\\', '/').replace(':', ':/')

# 查看 json 文件是否已存在
def json_file_exists():
    if os.path.exists(json_cwd):
        os.remove(json_cwd)

# 获取相册数据信息
def get_galleries_data():
    global galleries_name
    galleries_name = []
    # 查询相册目录下所有内容
    response = client.list_objects(
        Bucket= bucket_name,
        Prefix= photos_name,
        Delimiter='/',
    )
    CommonPrefixes = response['CommonPrefixes']
    for Prefixes in CommonPrefixes:
        Prefix = Prefixes['Prefix']
        gallery_name = Prefix.split("/")[1]
        galleries_name.append(gallery_name)
        # 查询相册目录下所有子文件夹内容
        response = client.list_objects(
            Bucket= bucket_name,
            Prefix= photos_name + gallery_name + '/',
            Delimiter='/',
        )
        contents = response['Contents']
        # 子文件夹所有照片添加到 photos_list 列表
        photos_list = []
        for i in range(len(contents)):
            content = contents[i]['Key'].split("/")[2]
            photos_list.append(content)
        del photos_list[0]
        # 相册添加到 gallery_dict 字典中
        gallery_dict = dict(name=1, cover=1, description=1, photos=1)
        gallery_dict.update(name = gallery_name)
        gallery_dict.update(cover = photos_list[0])
        gallery_dict.update(photos = photos_list[0:])
        photos_list.clear()
        # 所有相册添加到 galleries 列表中
        galleries.append(gallery_dict)
    print("生成相册数据完成")

# 数据写入
def galleries_data_write():
    with open(json_cwd, 'w', encoding='utf-8') as file:
        # 修整数据格式
        data0 = str(galleries).replace("}, {" , "},\n {")
        data1 = data0.replace("[{", "[\n {")
        data = data1.replace("}]", "}\n]")
        file.write(data)
        print("数据写入完成")

# 创建文件夹
def mkdir_galleries(file):
    if os.path.exists(file):
        shutil.rmtree(file)
    os.mkdir(file)

# # 创建二级相册目录和对应的index.md文件
def galleries_index():
    for name in galleries_name:
        gallery_index_dict= dict(title = name, layout = 'photo', comments = "false")
        mkdir_galleries(name)
        gallery_index_cwd = os.path.join(os.getcwd(), name , "index.md").replace('\\', '/').replace(':', ':/')
        with open(gallery_index_cwd, 'w', encoding='utf-8') as file:
            data0 = str(gallery_index_dict)
            data1 = data0.replace("{", "---\n").replace(",","\n").replace("}", "\n---")
            data = data1.replace("'", "").replace("photo",'''"photo"''').replace(" layout","layout").replace(" comments","comments")
            file.write(data)
    print("index数据写入完成")

if __name__ == "__main__":
    json_file_exists()      # 查看 json 文件是否已存在
    get_galleries_data()    # 获取相册数据信息
    galleries_data_write()    # 图像数据写入
    galleries_index()         # 创建二级相册目录和对应的index.md文件