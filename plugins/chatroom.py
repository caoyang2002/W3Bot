import pywxdll
import yaml
from loguru import logger
from utils.plugin_interface import PluginInterface
from utils.chatroom_database import ChatroomDatabase

class chatroom(PluginInterface):
    def __init__(self):
        config_path = 'plugins/chatroom.yml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f.read())
        self.plugin_setting = config['plugin_setting']

        main_config_path = 'main_config.yml'
        with open(main_config_path, 'r', encoding='utf-8') as f:
            main_config = yaml.safe_load(f.read())

        self.bot_version = main_config["bot_version"]
        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        # 初始化数据库连接
        self.db = ChatroomDatabase()

    async def run(self, recv):
        group_wxid = recv['from'] # chatroom id
        user_wxid = recv['sender'] # wxid
        username = recv['displayFullContent'].split(":")[0] # name
        content = recv.get('content', '') # content
        msg_type = recv.get('type', 'Unknown') # message type

        # 添加消息到数据库
        self.db.add_message(group_wxid, user_wxid, username, content, msg_type)

        # 查询用户信息
        user_data = self.db.get_user_data(group_wxid, user_wxid)

        if user_data:
            fields = ["群组ID", "用户ID"]
            out_message = "用户信息:\n"
            for i, field in enumerate(fields):
                if i < len(user_data):
                    value = user_data[i]
                    out_message += f"{field}: {value}\n"
        else:
            out_message = f"未找到用户 {user_wxid} 的信息。"

         logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
        self.bot.send_text_msg(recv["from"], out_message)  # 发送

      