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
        username = recv.get('senderName', user_wxid)
        content = recv.get('content', '')
        msg_type = recv.get('type', 'Unknown')

        # 检查群组是否存在，如果不存在则创建
        if recv['fromType'] == 'chatroom':
            group_info = self.db.get_group_info(group_wxid)
            if not group_info:
                group_name = recv.get('signature', {}).get('msgsource', {}).get('membercount', '未知群组')
                self.db.create_group(group_wxid, f"群组({group_name})")
                logger.info(f"创建新群组: {group_wxid}, 名称: 群组({group_name})")

        # 添加消息到数据库
        self.db.add_message(group_wxid, user_wxid, username, content, msg_type)

        # 查询用户信息
        user_data = self.db.get_user_data(group_wxid, user_wxid)

        if user_data:
            fields = [
                "群组ID", "用户ID", "用户名", "最后消息内容", "最后消息时间", "最后消息类型"
            ]
            out_message = "用户信息:\n"
            for i, field in enumerate(fields):
                if i < len(user_data):
                    value = user_data[i]
                    out_message += f"{field}: {value}\n"
        else:
            out_message = f"未找到用户 {user_wxid} 的信息。"

        logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
        self.bot.send_txt_msg(recv['from'], out_message)

        # 插件设置信息
        plugin_info = f"\n\n插件设置: {self.plugin_setting}"
        self.bot.send_txt_msg(recv['from'], plugin_info)