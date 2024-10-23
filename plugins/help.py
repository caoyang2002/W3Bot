import aiohttp
import yaml
from bs4 import BeautifulSoup as bs
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class help(PluginInterface):
    def __init__(self):
        config_path = "plugins/help.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        # self.important_news_count = config["important_news_count"]  # 要获取的要闻数量

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.help_message = config["help_message"]  # 帮助信息

    async def run(self, recv):
        try:
      
            self.bot.send_text_msg(recv["from"], self.help_message)
            logger.info(f'[发送信息]{self.help_message}| [发送到] {recv["from"]}')

        except Exception as error:
            out_message = f'获取帮助失败!⚠️\n{error}'
            self.bot.send_text_msg(recv["from"], out_message)
            logger.error(f'[发送信息]{out_message}| [发送到] {recv["from"]}')

  