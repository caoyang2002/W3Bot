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
        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)

        # 初始化数据库连接
        self.db = ChatroomDatabase()

    async def run(self, recv):
        group_wxid = recv['from'] if recv['fromType'] == 'chatroom' else 'private'
        user_wxid = recv['sender']
        username = recv.get('senderName', 'Unknown')
        message_content = recv.get('content', '')
        message_type = recv.get('type', 'Unknown')

        # 添加或更新用户信息
        self.db.add_or_update_user(group_wxid, user_wxid, username, message_content, message_type)

        # 查询用户信息
        user_data = self.db.get_user_data(group_wxid, user_wxid)

        if user_data:
            fields = [
                "群组ID", "用户ID", "用户名", "最后消息内容", "最后消息时间", "最后消息类型",
                "加入时间", "昵称修改次数", "白名单状态", "黑名单状态", "警告状态", "机器人置信度"
            ]
            out_message = "用户信息:\n"
            for i, field in enumerate(fields):
                if i < len(user_data):
                    value = user_data[i]
                    if field in ["白名单状态", "黑名单状态", "警告状态"]:
                        value = "是" if value else "否"
                    out_message += f"{field}: {value}\n"
        else:
            out_message = f"未找到用户 {user_wxid} 的信息。"

        logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
        self.bot.send_txt_msg(recv['from'], out_message)

        # 插件设置信息
        plugin_info = f"\n\n插件设置: {self.plugin_setting}"
        self.bot.send_txt_msg(recv['from'], plugin_info)