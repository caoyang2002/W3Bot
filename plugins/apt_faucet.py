import yaml
from loguru import logger
import pywxdll
from utils.plugin_interface import PluginInterface
from sdk.aptos_python.async_client import FaucetClient, RestClient
from sdk.aptos_python.account_address import AccountAddress
from typing import Tuple, Optional, Dict

class apt_faucet(PluginInterface):
    def __init__(self):
        # 加载插件配置
        config_path = "plugins/apt_faucet.yml"
        with open(config_path, "r", encoding="utf-8") as f:
            self.plugin_config = yaml.safe_load(f.read())

        # 网络配置
        self.networks = {
            "testnet": {
                "node_url": self.plugin_config.get("testnet_node_url", "https://fullnode.testnet.aptoslabs.com/v1"),
                "faucet_url": self.plugin_config.get("testnet_faucet_url", "https://faucet.testnet.aptoslabs.com")
            },
            "devnet": {
                "node_url": self.plugin_config.get("devnet_node_url", "https://fullnode.devnet.aptoslabs.com/v1"),
                "faucet_url": self.plugin_config.get("devnet_faucet_url", "https://faucet.devnet.aptoslabs.com")
            }
        }

        # 默认使用 testnet
        self.current_network = "testnet"
        self.set_network(self.current_network)

        # 加载主配置
        self.config = self.load_config()
        self.bot = pywxdll.Pywxdll(self.config["ip"], self.config["port"])

    def set_network(self, network: str):
        """设置当前网络"""
        network = network.lower()
        if network not in self.networks:
            raise ValueError(f"不支持的网络: {network}")
        
        self.current_network = network
        network_config = self.networks[network]
        self.rest_client = RestClient(network_config["node_url"])
        self.faucet_client = FaucetClient(network_config["faucet_url"], self.rest_client)

    def load_config(self):
        """加载主配置文件"""
        try:
            with open("main_config.yml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f.read())
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    def parse_command(self, content: list) -> Tuple[str, float, str]:
        """
        解析命令参数
        返回: (network, amount, address)
        """
        network = "testnet"  # 默认网络
        amount = 10.0  # 默认金额
        address = None

        try:
            # 移除命令名 (/gas)
            args = [arg for arg in content[1:] if arg.strip()]

            if not args:
                raise ValueError("缺少参数")

            current_pos = 0
            
            # 检查是否指定网络
            if args[current_pos].lower() in ["dev", "devnet"]:
                network = "devnet"
                current_pos += 1
            elif args[current_pos].lower() in ["test", "testnet"]:
                network = "testnet"
                current_pos += 1

            # 检查剩余参数
            remaining_args = args[current_pos:]
            
            if len(remaining_args) == 1:
                # 只有地址
                address = remaining_args[0]
            elif len(remaining_args) == 2:
                # 金额和地址
                amount = float(remaining_args[0])
                address = remaining_args[1]
            else:
                raise ValueError("参数格式错误")

            # 验证地址格式
            if not address.startswith("0x"):
                raise ValueError("地址必须以 0x 开头")

            return network, amount, address

        except ValueError as e:
            raise ValueError(f"命令解析错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"命令解析错误: {str(e)}")

    async def run(self, recv):
        try:
            content = [item for item in recv["content"] if item.strip()]
            logger.info(f"收到命令: {content}")

            if len(content) < 2:
                return await self.send_help(recv)

            # 解析命令
            network, amount, address = self.parse_command(content)
            
            # 设置网络
            self.set_network(network)
            
            # 转换金额为 octas
            amount_octas = int(amount * 1_000_000_000)
            
            # 处理请求
            await self.process_faucet(recv, address, amount_octas)

        except ValueError as e:
            await self.send_error(recv, str(e))
        except Exception as e:
            logger.error(f"处理命令时发生错误: {e}")
            await self.send_error(recv, f"处理命令失败: {e}")

    async def process_faucet(self, recv, address, amount):
        """处理水龙头请求"""
        try:
            account_address = AccountAddress.from_str(address)
            await self.faucet_client.fund_account(account_address, amount)
            balance = await self.rest_client.account_balance(account_address)
            await self.send_success(recv, address, amount, balance)
        except Exception as e:
            logger.error(f"领取 Gas 时发生错误: {e}")
            await self.send_error(recv, f"领取 Gas 失败: {e}")

    async def send_success(self, recv, address, amount, balance):
        """发送成功消息"""
        # 转换为可读格式
        amount_apt = amount / 100_000_000
        balance_apt = balance / 100_000_000
        formatted_address = f"{address[:6]}...{address[-6:]}" if len(address) > 12 else address
      
        success_msg = (
            f"\n✅ Gas 领取成功！\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🌐 网络: {self.current_network.upper()}\n"
            f"📜 地址: {formatted_address}\n"
            f"💧 领取: {amount_apt:.2f} APT\n"
            f"💰 余额: {balance_apt:.2f} APT\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔍 浏览器: https://explorer.aptoslabs.com/account/{address}?network={self.current_network}"
        )

        await self.send_message(recv, success_msg)

    async def send_message(self, recv, message, log_level="info"):
        """发送消息的通用方法"""
        getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
        self.bot.send_text_msg(recv["from"], message)

    async def send_error(self, recv, message):
        """
        发送错误消息
        :param recv: 接收消息的信息
        :param message: 错误信息
        """
        error_msg = (
            f"\n❌ 操作失败\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📛 错误信息：{message}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💡 输入 /gas 查看帮助"
        )
        await self.send_message(recv, error_msg, "error")

    async def send_help(self, recv):
        """发送帮助信息"""
        help_message = (
            f"\n🌊 Aptos Gas 领取助手\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📝 命令格式：\n\n"
            f"1️⃣ 默认领取 10 APT (testnet):\n"
            f"   /gas 0x<地址>\n\n"
            f"2️⃣ 指定数量:\n"
            f"   /gas <数量> 0x<地址>\n\n"
            f"3️⃣ 指定网络:\n"
            f"   /gas <网络> <数量> 0x<地址>\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🌐 支持的网络:\n"
            f"• testnet (test)\n"
            f"• devnet (dev)\n\n"
            f"📌 示例:\n"
            f"/gas test 10 0x123...\n"
            f"/gas dev 5 0x123...\n"
            f"━━━━━━━━━━━━━━━"
        )
        await self.send_message(recv, help_message)

    def format_address(self, address: str, length: int = 6) -> str:
        """
        格式化地址显示
        :param address: 完整地址
        :param length: 保留前后的字符数
        :return: 格式化后的地址
        """
        if len(address) <= length * 2:
            return address
        return f"{address[:length]}...{address[-length:]}"