# import os
# import time

# import aiohttp
# import yaml
# from loguru import logger

# import pywxdll
# from utils.plugin_interface import PluginInterface


# class chatroom(PluginInterface):
#     def __init__(self):
#         config_path = "plugins/chatroom.yml"
#         with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
#             config = yaml.safe_load(f.read())

#         self.chatroom_url = config["chatroom_url"]  # 随机图片api

#         main_config_path = "main_config.yml"
#         with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
#             main_config = yaml.safe_load(f.read())

#         self.ip = main_config["ip"]  # 机器人ip
#         self.port = main_config["port"]  # 机器人端口
#         self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

#         cache_path = "resources/cache"  # 检测是否有cache文件夹
#         if not os.path.exists(cache_path):
#             logger.info("检测到未创建cache缓存文件夹")
#             os.makedirs(cache_path)
#             logger.info("已创建cache文件夹")

#     async def run(self, recv):
#         current_directory = os.path.dirname(os.path.abspath(__file__))

#         cache_path_original = os.path.join(
#             current_directory, f"../resources/cache/picture_{time.time_ns()}"
#         )  # 图片缓存路径

#         try:
#             conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
#             async with aiohttp.request(
#                     "GET", url=self.chatroom_url, connector=conn_ssl
#             ) as req:
#                 cache_path = (
#                     cache_path_original +
#                     req.headers["Content-Type"].split("/")[1]
#                 )
#                 with open(cache_path, "wb") as file:  # 下载并保存
#                     file.write(await req.read())
#                     file.close()
#                 await conn_ssl.close()

#             logger.info(
#                 f'[发送信息](随机图图图片) {cache_path}| [发送到] {recv["from"]}'
#             )
#             self.bot.send_image_msg(
#                 recv["from"], os.path.abspath(cache_path)
#             )  # 发送图片

#         except Exception as error:
#             out_message = f"-----XYBot-----\n出现错误❌！{error}"
#             logger.error(error)
#             logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
#             self.bot.send_text_msg(recv["from"], out_message)  # 发送

import pywxdll
import yaml
from loguru import logger
from utils.plugin_interface import PluginInterface
from utils.chatroom_database import ChatroomDatabase

# 适配 XYBot v0.0.6


class chatroom(PluginInterface):
    def __init__(self):
        config_path = 'plugins/chatroom.yml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f.read())
        self.plugin_setting = config['plugin_setting']

        main_config_path = 'main_config.yml'
        with open(main_config_path, 'r', encoding='utf-8') as f:
            main_config = yaml.safe_load(f.read())
        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)

        # 初始化数据库连接
        self.db = ChatroomDatabase()

    async def run(self, recv):
        group_wxid = recv['from'] if recv['fromType'] == 'chatroom' else 'private'
        user_wxid = recv['sender']

        # 查询用户信息
        user_data = self.db.get_user_data(group_wxid, user_wxid)

        if user_data:
            # 解包用户数据
            (_, _, username, _, message_timestamp, message_type, join_time,
             nickname_change_count, is_whitelist, is_blacklist, is_warned,
             bot_confidence, daily_message_count) = user_data

            out_message = (
                f"用户信息:\n"
                f"用户名: {username}\n"
                f"加入时间: {join_time}\n"
                f"昵称修改次数: {nickname_change_count}\n"
                f"每日消息数: {daily_message_count}\n"
                f"白名单状态: {'是' if is_whitelist else '否'}\n"
                f"黑名单状态: {'是' if is_blacklist else '否'}\n"
                f"警告状态: {'是' if is_warned else '否'}\n"
                f"机器人置信度: {bot_confidence}\n"
                f"最后消息时间: {message_timestamp}\n"
                f"最后消息类型: {message_type}"
            )
        else:
            out_message = f"未找到用户 {user_wxid} 的信息。"

        logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
        self.bot.send_txt_msg(recv['from'], out_message)

        # 插件设置信息
        plugin_info = f"\n\n插件设置: {self.plugin_setting}"
        self.bot.send_txt_msg(recv['from'], plugin_info)
