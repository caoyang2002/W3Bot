import base64

import yaml
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class bot_status(PluginInterface):
    def __init__(self):
        config_path = "plugins/bot_status.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.status_message = config["status_message"]  # 状态信息
        self.github = config["github"] # github 地址
        self.docker = config["docker"] # docker 地址

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.bot_version = main_config["bot_version"]

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):

        out_message = f"-----XYBot-----\n{self.status_message}\nBot version: {self.bot_version}\nRepo: {self.github}\n Docker: {self.docker}"
        logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
        self.bot.send_text_msg(recv["from"], out_message)  # 发送
