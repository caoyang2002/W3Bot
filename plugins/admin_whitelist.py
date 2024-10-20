import yaml
from loguru import logger
import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface

class admin_whitelist(PluginInterface):
    def __init__(self):
        self.config = self.load_config()
        self.bot = pywxdll.Pywxdll(self.config["ip"], self.config["port"])
        self.admin_list = self.config["admins"]
        self.db = BotDatabase()

    def load_config(self):
        try:
            with open("main_config.yml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f.read())
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    async def run(self, recv):
        admin_wxid = recv["sender"]
        content = [item for item in recv["content"] if item.strip()]  # 移除空字符串

        logger.info(f"收到白名单管理命令: {content}")

        if len(content) < 3:
            return await self.send_help(recv)

        if admin_wxid not in self.admin_list:
            return await self.send_error(recv, "你没有权限使用此指令")

        wxid = self.get_wxid(content)
        if not wxid:
            return await self.send_error(recv, "无法获取用户ID，请确保正确使用@或wxid")

        action = content[-1]  # 取最后一个非空元素作为操作

        await self.process_action(recv, wxid, action)

    def get_wxid(self, content):
        for item in content[1:]:  # 从第二个元素开始查找
            if item.startswith('@'):
                return item[1:]  # 移除@符号
            elif item.startswith('wxid_'):
                return item
        return None

    async def process_action(self, recv, wxid, action):
        try:
            if action == "加入":
                self.db.set_whitelist(wxid, 1)
                await self.send_success(recv, wxid, "加入")
            elif action == "删除":
                self.db.set_whitelist(wxid, 0)
                await self.send_success(recv, wxid, "删除")
            else:
                await self.send_error(recv, f"未知的操作: {action}")
        except Exception as e:
            logger.error(f"执行白名单操作时发生错误: {e}")
            await self.send_error(recv, f"操作失败: {e}")

    async def send_message(self, recv, message, log_level="info"):
        getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
        self.bot.send_text_msg(recv["from"], message)

    async def send_help(self, recv):
        help_message = (
            "\n帮助信息:\n"
            "有白名单者使用 ChatGPT 不扣积分\n\n"
            "指令: \n"
            "管理白名单 @ 加入/删除\n"
            "如: 管理白名单 @W3Bot 加入\n"
            "管理白名单 @W3Bot 删除\n"
            "或\n"
            "管理白名单 wxid_xxx 加入\n"
            "管理白名单 wxid_xxx 删除"
        )
        await self.send_message(recv, help_message)

    async def send_error(self, recv, message):
        await self.send_message(recv, f"\n❌ {message}", "error")

    async def send_success(self, recv, wxid, action):
        await self.send_message(recv, f"\n成功{action}{wxid}到白名单！😊")
