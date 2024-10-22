import yaml
from loguru import logger
import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
import asyncio
from sdk.aptos_python.async_client import FaucetClient, RestClient
from sdk.aptos_python.account import Account
from sdk.aptos_python.account_address import AccountAddress



class apt_faucet(PluginInterface):
    def __init__(self):
        self.config = self.load_config()
        self.bot = pywxdll.Pywxdll(self.config["ip"], self.config["port"])
        self.faucet_url= self.config["faucet_url"]
        self.node_url = self.config["node_url"]
        # self.db = BotDatabase()
        self.rest_client = RestClient("https://api.testnet.aptoslabs.com/v1")
        self.faucet_client = FaucetClient("https://faucet.testnet.aptoslabs.com", self.rest_client)

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



        wxid = self.get_wxid(content)
        if not wxid:
            return await self.send_error(recv, "无法获取用户ID，请确保正确使用@或wxid")

        action = content[-1]  # 取最后一个非空元素作为操作



    def get_wxid(self, content):
        for item in content[1:]:  # 从第二个元素开始查找
            if item.startswith('@'):
                return item[1:]  # 移除@符号
            elif item.startswith('wxid_'):
                return item
        return None



    async def send_message(self, recv, message, log_level="info"):
        getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
        self.bot.send_text_msg(recv["from"], message)

    async def send_help(self, recv):
        help_message = (
            "\n帮助信息:\n"
            "在指定的地址领取 Gas，默认在 testnet 领取 10 个 Gas\n\n"
            "指令: \n"
            "领取 10 个 gas"
            "/gas 0x123456789\n"
            "领取 5 个 gas "
            "/gas 5 0x123456789"
            "在 devnet 领取"
            "/gas dev 5 0x12345678"

        )
        await self.send_message(recv, help_message)

    async def send_error(self, recv, message):
        await self.send_message(recv, f"\n❌ {message}", "error")

    async def send_success(self, recv, wxid, action):
        await self.send_message(recv, f"\n成功{action}{wxid}到白名单！😊")
