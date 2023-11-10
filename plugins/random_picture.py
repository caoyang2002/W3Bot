import os

import pywxdll
import requests
import yaml
from PIL import Image
from loguru import logger

from plugin_interface import PluginInterface


class random_picture(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.random_picture_url = config['random_picture_url']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

        self.img_exp = ".png"  # 微信不支持直接发webp

    def run(self, recv):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        pic_cache_path_original = os.path.join(current_directory, '../pic_cache/picture.')  # 服务器的绝对路径，非客户端
        r = requests.get(self.random_picture_url)
        pic_cache_path = pic_cache_path_original + r.headers['Content-Type'].split('/')[1]
        with open(pic_cache_path, 'wb') as f:  # 下载并保存
            f.write(r.content)
            f.close()

        # 把图片转成png
        img = Image.open(pic_cache_path)
        img.load()
        img.save(pic_cache_path_original + self.img_exp)

        pic_cache_path = pic_cache_path_original + self.img_exp

        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message="(随机图图图片)", wxid=recv['wxid']))
        self.bot.send_pic_msg(recv['wxid'], os.path.abspath(pic_cache_path))  # 发送图片
