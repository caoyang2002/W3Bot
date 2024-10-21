import yaml
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface

class admin_points(PluginInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]
        self.port = main_config["port"]
        self.bot = pywxdll.Pywxdll(self.ip, self.port)
        self.admin_list = main_config["admins"]
        self.db = BotDatabase()

    @staticmethod
    def is_number(s):
        if isinstance(s, str):
            s = s.strip()
            if s.isdigit():
                return True
            if s.startswith('+') or s.startswith('-'):
                return s[1:].isdigit()
            try:
                float(s)
                return True
            except ValueError:
                return False
        return False

    async def run(self, recv):
        admin_wxid = recv["sender"]
        content = recv["content"]

        logger.info(f"收到管理积分命令: {content}")

        if admin_wxid not in self.admin_list:
            logger.warning(f"非管理员 {admin_wxid} 尝试使用管理积分命令")
            return await self.send_error(recv, "❌ 该指令为管理员功能，您还未被添加到管理员列表")

        if len(content) < 3:
            logger.error(f"命令参数不足: {content}")
            return await self.send_error(recv, self.get_error_message())

        change_wxid = self.get_change_wxid(recv)
        if not change_wxid:
            logger.error(f"无法识别目标用户: {content[1]}")
            return await self.send_error(recv, "❌ 无法识别目标用户，请确保使用正确的 @mention 或 wxid")

        await self.handle_points(recv, change_wxid, content[2:])

    def get_change_wxid(self, recv):
        content = recv["content"]
        if content[1].startswith('@'):
            if 'atUserList' in recv and recv['atUserList']:
                return recv['atUserList'][0]
            else:
                logger.error(f"使用了 @mention 但 atUserList 为空: {content}")
                return None
        elif content[1].startswith('wxid_'):
            return content[1]
        logger.error(f"无法识别的用户标识: {content[1]}")
        return None

    async def handle_points(self, recv, change_wxid, args):
        # 移除空字符串元素并合并剩余元素
        args = [arg for arg in args if arg.strip()]
        value = ''.join(args)

        if self.is_number(value):
            await self.process_points(recv, change_wxid, value)
        elif len(args) == 2 and args[0] in ['加', '减'] and self.is_number(args[1]):
            value = f"+{args[1]}" if args[0] == '加' else f"-{args[1]}"
            await self.process_points(recv, change_wxid, value)
        else:
            await self.send_error(recv, f"❌ 无效的操作或积分值: {' '.join(args)}")

    async def process_points(self, recv, change_wxid, value):
        try:
            if value.startswith('+') or value.startswith('-'):
                points = int(value)
                self.db.add_points(change_wxid, points)
                operation = "增加" if points > 0 else "减少"
                logger.info(f"为用户 {change_wxid} {operation}了 {abs(points)} 积分")
            else:
                points = int(value)
                self.db.set_points(change_wxid, points)
                logger.info(f"将用户 {change_wxid} 的积分设置为 {points}")
            await self.send_result(recv, change_wxid, value)
        except Exception as e:
            logger.error(f"处理积分时发生错误: {e}")
            await self.send_error(recv, f"处理积分时发生错误: {e}")

    async def send_result(self, recv, change_wxid, operation):
        try:
            total_points = self.db.get_points(change_wxid)
            if operation.startswith('+'):
                out_message = f'\n😊 成功给{change_wxid}增加了{operation[1:]}点积分！他现在有{total_points}点积分！'
            elif operation.startswith('-'):
                out_message = f'\n😊 成功给{change_wxid}减少了{operation[1:]}点积分！他现在有{total_points}点积分！'
            else:
                out_message = f'\n😊 成功将{change_wxid}的积分设置为{operation}！他现在有{total_points}点积分！'
            logger.info(f'发送结果: {out_message}')
            self.bot.send_text_msg(recv["from"], out_message)
        except Exception as e:
            logger.error(f"发送结果时发生错误: {e}")
            await self.send_error(recv, f"发送结果时发生错误: {e}")

    async def send_error(self, recv, message):
        logger.error(f'发送错误: {message}')
        self.bot.send_text_msg(recv["from"], message)

    @staticmethod
    def get_error_message():
        return "\n⚠️ 指令格式错误！\n使用方法:\n增加积分：/管理积分 @用户名 +10 或 /管理积分 @用户名 加 10\n减少积分：/管理积分 @用户名 -10 或 /管理积分 @用户名 减 10\n设置积分：/管理积分 @用户名 10"
