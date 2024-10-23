import os
import random
import time
import asyncio
from typing import Optional, Dict, List
from datetime import datetime

import yaml
from captcha.image import ImageCaptcha
from loguru import logger
import pywxdll
from sdk.aptos_python import ed25519
from sdk.aptos_python.account import Account
from sdk.aptos_python.account_address import AccountAddress
from sdk.aptos_python.asymmetric_crypto import PrivateKey
from sdk.aptos_python.async_client import RestClient
from utils.aptos_user_database import AptosUserDatabase
from utils.plugin_interface import PluginInterface

class aptos_airdrop(PluginInterface):
    def __init__(self):
        """初始化空投系统"""
        # 主配置
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]
        self.port = main_config["port"]
        self.bot = pywxdll.Pywxdll(self.ip, self.port)
        self.bot_private_key = main_config["aptos_private_key"]

        # 读取红包配置
        config_path = "plugins/aptos_airdrop.yml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 红包基础配置
        self.max_point = config["max_point"]  
        self.min_point = config["min_point"]  
        self.max_packet = config["max_packet"]  
        self.max_time = config["max_time"]
        self.node_url = config["node_url"]

        # 初始化数据库和客户端
        self.db = AptosUserDatabase()
        self.rest_client = RestClient(self.node_url)

        try:
            # 创建机器人账户
            self.bot_account = self.create_account_from_private_key(self.bot_private_key)
            logger.info(f"Bot account address: {self.bot_account.address()}")
        except Exception as e:
            logger.error(f"Failed to create bot account: {e}")
            raise

        # 初始化红包存储
        self.red_packets = {}
        
        # 创建缓存目录
        cache_path = "resources/cache"
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
            logger.info("Created cache directory")

    @staticmethod
    def create_account_from_private_key(private_key: str) -> Account:
        """从私钥创建账户"""
        private_key = PrivateKey.from_str(private_key)
        account_address = AccountAddress.from_key(private_key.public_key())
        return Account(account_address, private_key)

    @staticmethod
    def normalize_address(address: str) -> str:
        """标准化地址格式"""
        if not address.startswith("0x"):
            return f"0x{address}"
        return address

    async def transfer_apt(self, from_account: Account, to_address: str, amount: int) -> str:
        """执行APT转账"""
        try:
            to_address = self.normalize_address(to_address)
            txn_hash = await self.rest_client.bcs_transfer(
                from_account,
                AccountAddress.from_str(to_address),
                amount
            )
            await self.rest_client.wait_for_transaction(txn_hash)
            return txn_hash
        except Exception as e:
            logger.error(f"Transfer error: {str(e)}")
            raise

    async def run(self, recv):
        """处理命令"""
        command = recv["content"][0]

        if command in ["/发红包", "/airdrop"]:
            await self.send_red_packet(recv)
        elif command in ["/抢红包", "/claim"]:
            await self.grab_red_packet(recv)
        else:
            self.send_message(recv, "❌命令格式错误！请查看菜单获取正确命令格式")

    async def send_red_packet(self, recv):
        """发送红包"""
        sender = recv["sender"]
        content = recv["content"]

        # 参数验证
        if len(content) < 3:
            self.send_message(recv, "❌参数不足! 格式: /发红包 金额 数量 [可选:钱包地址]")
            return

        try:
            amount = float(content[1])
            count = int(content[2])
            wallet_address = content[3] if len(content) > 3 else None
        except ValueError:
            self.send_message(recv, "❌参数格式错误！金额和数量必须是数字")
            return

        # 验证参数
        if amount > self.max_point or amount < self.min_point:
            self.send_message(recv, f"❌金额超出范围! 最小{self.min_point}, 最大{self.max_point}")
            return
        if count > self.max_packet:
            self.send_message(recv, f"❌红包数量超出上限{self.max_packet}!")
            return
            
        # 获取或更新钱包地址
        user_data = self.db.get_user_data(sender)
        if wallet_address:
            wallet_address = self.normalize_address(wallet_address)
            try:
                # 验证地址格式
                AccountAddress.from_str(wallet_address)
                self.db.update_user_field(sender, "wallet_address", wallet_address)
                sender_address = wallet_address
            except ValueError:
                self.send_message(recv, "❌钱包地址格式错误！")
                return
        elif user_data and user_data.get("wallet_address"):
            sender_address = user_data["wallet_address"]
        else:
            self.send_message(recv, "❌请先设置钱包地址!")
            return

        try:
            # 检查余额
            balance = await self.rest_client.account_balance(sender_address)
            total_octas = int(amount * 100_000_000)
            
            if balance < total_octas:
                self.send_message(recv, f"❌余额不足! 当前余额: {balance/100_000_000:.8f} APT")
                return

            # 生成红包
            amounts = self.split_amount(total_octas, count)
            captcha, captcha_path = self.generate_captcha()
            
            # 存储红包信息
            self.red_packets[captcha] = {
                "sender": sender,
                "sender_address": sender_address,
                "total_amount": amount,
                "amounts": amounts,
                "claimed": [],
                "timestamp": time.time(),
                "room": recv["from"]
            }

            # 执行转账
            txn_hash = await self.transfer_apt(
                self.bot_account,
                sender_address,
                total_octas
            )

            # 发送消息
            nickname = recv.get("sender_nick", sender)
            message = f"""
🎉 {nickname} 发送了一个红包!
💰 总金额: {amount} APT
📦 数量: {count} 个
🔗 交易hash: {txn_hash}
            
请使用 /抢红包 验证码 [可选:钱包地址] 来领取
            """
            self.send_message(recv, message)
            self.bot.send_image(recv["from"], captcha_path)

        except Exception as e:
            logger.error(f"发送红包错误: {str(e)}")
            self.send_message(recv, "❌发送红包失败，请稍后重试!")

    async def grab_red_packet(self, recv):
        """抢红包"""
        grabber = recv["sender"]
        content = recv["content"]

        if len(content) < 2:
            self.send_message(recv, "❌参数不足! 格式: /抢红包 验证码 [可选:钱包地址]")
            return

        captcha = content[1]
        wallet_address = content[2] if len(content) > 2 else None

        # 验证红包
        if captcha not in self.red_packets:
            self.send_message(recv, "❌红包不存在或已过期!")
            return

        packet = self.red_packets[captcha]
        
        # 验证状态
        if grabber in packet["claimed"]:
            self.send_message(recv, "❌您已经抢过这个红包了!")
            return
        if not packet["amounts"]:
            self.send_message(recv, "❌红包已被抢完!")
            return
        if time.time() - packet["timestamp"] > self.max_time:
            self.send_message(recv, "❌红包已过期!")
            return

        # 获取钱包地址
        user_data = self.db.get_user_data(grabber)
        if wallet_address:
            wallet_address = self.normalize_address(wallet_address)
            try:
                AccountAddress.from_str(wallet_address)
                self.db.update_user_field(grabber, "wallet_address", wallet_address)
                grabber_address = wallet_address
            except ValueError:
                self.send_message(recv, "❌钱包地址格式错误！")
                return
        elif user_data and user_data.get("wallet_address"):
            grabber_address = user_data["wallet_address"]
        else:
            self.send_message(recv, "❌请先设置钱包地址!")
            return

        try:
            # 获取红包金额
            amount_octas = packet["amounts"].pop()
            
            # 执行转账
            txn_hash = await self.transfer_apt(
                self.bot_account,
                grabber_address,
                amount_octas
            )

            # 更新状态
            packet["claimed"].append(grabber)
            
            # 发送消息
            nickname = recv.get("sender_nick", grabber)
            amount_apt = amount_octas / 100_000_000
            self.send_message(
                recv, 
                f"""🎉 恭喜 {nickname} 抢到了 {amount_apt:.8f} APT!
🔗 交易hash: {txn_hash}"""
            )

            # 清理完成的红包
            if not packet["amounts"]:
                del self.red_packets[captcha]

        except Exception as e:
            logger.error(f"抢红包错误: {str(e)}")
            if 'amount_octas' in locals():
                packet["amounts"].append(amount_octas)
            self.send_message(recv, "❌领取红包失败，请稍后重试!")

    @staticmethod
    def generate_captcha(length=5):
        """生成验证码"""
        chars = "abdefghknpqtwxy23467889"
        code = "".join(random.sample(chars, length))
        image = ImageCaptcha().generate_image(code)
        path = f"resources/cache/{code}.jpg"
        image.save(path)
        return code, path

    @staticmethod
    def split_amount(total: int, count: int) -> List[int]:
        """随机分配红包金额"""
        min_amount = 10000  # 0.0001 APT
        remaining = total - min_amount * count
        
        if remaining < 0:
            raise ValueError("总金额不足以平均分配")

        amounts = []
        for i in range(count - 1):
            max_amount = remaining * 2 // (count - i)
            amount = random.randint(0, max_amount)
            amounts.append(amount + min_amount)
            remaining -= amount

        amounts.append(remaining + min_amount)
        random.shuffle(amounts)
        
        return amounts

    def send_message(self, recv, message):
        """发送消息"""
        if recv["fromType"] == "chatroom":
            self.bot.send_at_msg(recv["from"], message, [recv["sender"]])
        else:
            self.bot.send_text_msg(recv["from"], message)

    async def check_expired_packets(self):
        """检查过期红包"""
        for code in list(self.red_packets.keys()):
            packet = self.red_packets[code]
            if time.time() - packet["timestamp"] > self.max_time:
                if packet["amounts"]:
                    total_remaining_octas = sum(packet["amounts"])
                    try:
                        txn_hash = await self.transfer_apt(
                            self.bot_account,
                            packet["sender_address"],
                            total_remaining_octas
                        )
                        
                        total_remaining_apt = total_remaining_octas / 100_000_000
                        message = f"""
📢 红包 {code} 已过期
💰 剩余 {total_remaining_apt:.8f} APT 已退回给发送者
🔗 交易hash: {txn_hash}
                        """
                        self.bot.send_text_msg(packet["room"], message)
                    except Exception as e:
                        logger.error(f"退回红包失败: {e}")
                
                del self.red_packets[code]