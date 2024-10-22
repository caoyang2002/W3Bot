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
        config_path = "plugins/apt_faucet.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())
        self.node_url = config["node_url"]  
        self.faucet_url = config["faucet_url"] 

        self.config = self.load_config()
        self.bot = pywxdll.Pywxdll(self.config["ip"], self.config["port"])
        
 
        # self.db = BotDatabase()
        self.rest_client = RestClient(self.node_url)
        self.faucet_client = FaucetClient(self.faucet_url, self.rest_client)

    def load_config(self):
        """
        加载配置文件
        """
        try:
            with open("main_config.yml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f.read())
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    async def run(self, recv):
        # admin_wxid = recv["sender"]
        content = [item for item in recv["content"] if item.strip()]  # 移除空字符串

        logger.info(f"收到命令: {content}")

        # 检查命令参数
        if len(content) < 3:
            return await self.send_help(recv)



        wxid = self.get_wxid(content)
        if not wxid:
            return await self.send_error(recv, "无法获取用户ID，请确保正确使用@或wxid")

        # action = content[-1]  # 取最后一个非空元素作为操作
        amount, address = self.parse_command(content)
        if not address:
            return await self.send_error(recv, "无法获取有效的地址")

        await self.process_faucet(recv, address, amount)

    def get_wxid(self, content):
        for item in content[1:]:  # 从第二个元素开始查找
            if item.startswith('@'):
                return item[1:]  # 移除@符号
            elif item.startswith('wxid_'):
                return item
            elif item.startswith('0x'):
                return item
        return None

    def parse_command(self, content):
        amount = 10_000_000  # 默认 10 APT
        address = None
        
        if len(content) == 2:
            address = content[1]
        elif len(content) >= 3:
            try:
                amount = int(float(content[1]) * 100_000_000)  # 转换为 octas
                address = content[2]
            except ValueError:
                address = content[1]

        return amount, address
    async def process_faucet(self, recv, address, amount):
        """
        处理水龙头请求
        """
        try:
            account_address = AccountAddress.from_str(address)
            await self.faucet_client.fund_account(account_address, amount)
            balance = await self.rest_client.account_balance(account_address)
            await self.send_success(recv, address, amount, balance)
        except Exception as e:
            logger.error(f"领取 gas 时发生错误: {e}")
            await self.send_error(recv, f"领取 gas 失败: {e}")


    async def send_message(self, recv, message, log_level="info"):
        getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
        self.bot.send_text_msg(recv["from"], message)

    async def send_help(self, recv):
        help_message = (
            "\n帮助信息:\n"
            "在指定的地址领取 Gas，默认在 testnet 领取 10 个 Gas\n\n"
            "指令: \n"
            "领取 10 个 gas:\n"
            "/gas 0x123456789\n"
            "领取 5 个 gas:\n"
            "/gas 5 0x123456789\n"
            "在 devnet 领取:\n"
            "/gas dev 5 0x12345678\n"

        )
        await self.send_message(recv, help_message)

    async def send_error(self, recv, message):
        await self.send_message(recv, f"\n❌ {message}", "error")

    async def send_success(self, recv, wxid, action):
        await self.send_message(recv, f"\n成功{action}{wxid}到白名单！😊")
