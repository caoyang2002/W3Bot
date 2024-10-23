import os
import random
import time
import asyncio
from typing import Optional, Dict, List
from datetime import datetime
import traceback
import sys

import yaml
from captcha.image import ImageCaptcha
from loguru import logger
import pywxdll

from sdk.aptos_python.ed25519 import PrivateKey  # 直接使用 SDK 的 PrivateKey
from sdk.aptos_python.account import Account
from sdk.aptos_python.account_address import AccountAddress
from sdk.aptos_python.asymmetric_crypto import PrivateKey
from sdk.aptos_python.async_client import RestClient
from utils.aptos_user_database import AptosUserDatabase
from utils.plugin_interface import PluginInterface
from nacl.signing import SigningKey
from sdk.aptos_python import ed25519  # 使用具体的ed25519实现

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
    def create_account_from_private_key(key: str) -> Account:
        """从私钥创建 Aptos 账户"""
        try:
            # 记录初始输入（注意不要记录完整私钥）
            logger.info(f"开始创建账户 (私钥前4字符: {key[:4]}...)")

            # 移除前缀
            if key.startswith('0x'):
                key = key[2:]
                logger.info("已移除0x前缀")

            # 转换为字节
            try:
                key_bytes = bytes.fromhex(key)
                logger.info(f"私钥已转换为字节，长度: {len(key_bytes)}")
            except ValueError as e:
                logger.error(f"私钥格式错误: {str(e)}")
                raise
                
            # 创建 SigningKey
            try:
                signing_key = SigningKey(key_bytes)
                logger.info("SigningKey 创建成功")
            except Exception as e:
                logger.error(f"创建 SigningKey 失败: {str(e)}")
                raise

            # 创建 PrivateKey
            try:
                private_key = ed25519.PrivateKey(signing_key)
                logger.info("PrivateKey 创建成功")
            except Exception as e:
                logger.error(f"创建 PrivateKey 失败: {str(e)}")
                raise

            # 创建账户
            try:
                account_address = AccountAddress.from_key(private_key.public_key())
                account = Account(account_address, private_key)
                logger.info(f"账户创建成功，地址: {account.address()}")
                return account
            except Exception as e:
                logger.error(f"创建账户失败: {str(e)}")
                raise

        except Exception as e:
            logger.error("创建账户过程中发生错误:")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            logger.error("完整跟踪信息:")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def normalize_address(address: str) -> str:
        """标准化地址格式"""
        if not address.startswith("0x"):
            return f"0x{address}"
        return address

    async def transfer_apt(self, from_account: Account, to_address: str, amount: int) -> str:
        """从账户向指定地址转账"""
    
        try:
            # 打印转账参数
            logger.info(f"转账参数:")
            logger.info(f"- 发送方: {from_account.address()}")
            logger.info(f"- 接收方: {to_address}")
            logger.info(f"- 金额: {amount} Octas")

            # 验证并转换地址
            try:
                to_address_obj = AccountAddress.from_str(to_address)
                logger.info(f"地址转换成功: {to_address} -> {to_address_obj}")
            except Exception as addr_error:
                logger.error(f"地址转换失败: {str(addr_error)}")
                raise ValueError(f"无效的地址格式: {to_address}") from addr_error

            # 执行转账
            try:
                txn_hash = await self.rest_client.bcs_transfer(
                    from_account,
                    to_address_obj,
                    amount
                )
                logger.info(f"交易已提交，hash: {txn_hash}")
            except Exception as tx_error:
                logger.error(f"交易提交失败: {str(tx_error)}")
                logger.error(traceback.format_exc())
                raise

            # 等待交易确认
            try:
                await self.rest_client.wait_for_transaction(txn_hash)
                logger.info(f"交易已确认: {txn_hash}")
            except Exception as wait_error:
                logger.error(f"等待交易确认失败: {str(wait_error)}")
                raise

            return txn_hash

        except Exception as e:
            logger.error("转账过程中发生错误:")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            logger.error("完整跟踪信息:")
            logger.error(traceback.format_exc())
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
        try:
            sender = recv["sender"]
            content = recv["content"]

            # 参数验证
            if len(content) < 3:
                self.send_message(recv, "❌参数不足! 格式:\n/发红包 金额 数量 [可选:钱包地址]")
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
            # 获取或更新钱包地址
            user_data = self.db.get_user_data(sender)
            if wallet_address:
                wallet_address = self.normalize_address(wallet_address)
                try:
                    # 验证地址格式
                    sender_address_obj = AccountAddress.from_str(wallet_address)
                    self.db.update_user_field(sender, "wallet_address", wallet_address)
                    sender_address = wallet_address
                    logger.info(f"钱包地址已更新: {wallet_address}")
                except ValueError as e:
                    logger.error(f"地址格式错误: {str(e)}")
                    self.send_message(recv, "❌钱包地址格式错误！")
                    return
            elif user_data and user_data.get("wallet_address"):
                sender_address = user_data["wallet_address"]
                try:
                    sender_address_obj = AccountAddress.from_str(sender_address)
                    logger.info(f"使用现有钱包地址: {sender_address}")
                except ValueError as e:
                    logger.error(f"存储的地址格式错误: {str(e)}")
                    self.send_message(recv, "❌存储的钱包地址无效，请重新设置！")
                    return
            else:
                self.send_message(recv, "❌请先设置钱包地址!")
                return

            try:
                # 检查余额 - 使用 AccountAddress 对象
                logger.info(f"正在查询地址余额: {sender_address}")
                balance = await self.rest_client.account_balance(sender_address_obj)
                logger.info(f"余额查询成功: {balance/100_000_000:.8f} APT")

                total_octas = int(amount * 100_000_000)
                
                if balance < total_octas:
                    logger.info(f"余额不足: 需要 {amount} APT，当前有 {balance/100_000_000:.8f} APT")
                    self.send_message(recv, f"❌余额不足! 当前余额: {balance/100_000_000:.8f} APT")
                    return

                # 生成红包
                amounts = self.split_amount(total_octas, count)
                captcha, captcha_path = self.generate_captcha()
                
                # 在 send_red_packet 方法中存储红包信息时
                current_time = time.time()
                self.red_packets[captcha] = {
                    "sender": sender,
                    "sender_address": sender_address,
                    "total_amount": amount,
                    "amounts": amounts,
                    "claimed": [],
                    "timestamp": current_time,  # 使用当前时间
                    "room": recv["from"]
                }
                logger.info(f"创建红包: captcha={captcha}")
                logger.info(f"- 创建时间: {datetime.fromtimestamp(current_time)}")
                logger.info(f"- 过期时间: {datetime.fromtimestamp(current_time + self.max_time)}")

                logger.info(f"准备执行转账: {amount} APT -> {sender_address}")
                # 执行转账 - 也使用 AccountAddress 对象
                txn_hash = await self.transfer_apt(
                    self.bot_account,
                    sender_address_obj,  # 使用对象而不是字符串
                    total_octas
                )
                logger.info(f"转账成功，hash: {txn_hash}")

                # 发送消息
                nickname = recv.get("sender_nick", sender)
                message = f"""
    🎉 {nickname} 发送了一个红包!
    💰 总金额: {amount} APT
    📦 数量: {count} 个
    code: {captcha}
    🔗 交易hash: {txn_hash}
                
    请使用 /抢红包 验证码 [可选:钱包地址] 来领取
                """
                self.send_message(recv, message)
                logger.info(f"发送消息: {message}")
                self.bot.send_image_msg(recv["from"], captcha_path)
                logger.info(f"发送图片: {captcha_path}")

            except Exception as e:
                exc_info = sys.exc_info()
                logger.error("操作过程中发生错误:")
                logger.error(f"错误类型: {exc_info[0].__name__}")
                logger.error(f"错误信息: {str(e)}")
                logger.error("错误位置:")
                for frame in traceback.extract_tb(exc_info[2]):
                    logger.error(f"  文件 {frame.filename}, 第 {frame.lineno} 行")
                    logger.error(f"  在 {frame.name} 中: {frame.line}")
                logger.error("完整堆栈:")
                logger.error(traceback.format_exc())
                self.send_message(recv, "❌发送红包失败，请稍后重试!")

        except Exception as e:
            # 最外层错误处理
            logger.error(f"发送红包过程中发生未预期的错误: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_message(recv, "❌发送红包时发生错误，请联系管理员!")

    async def transfer_apt(self, from_account: Account, to_address: AccountAddress, amount: int) -> str:
        """
        执行APT转账
        :param from_account: 发送方账户
        :param to_address: 接收方地址对象
        :param amount: 金额(octas)
        :return: 交易哈希
        """
        try:
            logger.info(f"开始转账:")
            logger.info(f"- 发送方: {from_account.address()}")
            logger.info(f"- 接收方: {to_address}")
            logger.info(f"- 金额: {amount/100_000_000:.8f} APT")

            # 执行转账 - 直接使用 AccountAddress 对象
            txn_hash = await self.rest_client.bcs_transfer(
                from_account,
                to_address,  # 已经是 AccountAddress 对象
                amount
            )
            logger.info(f"交易已提交: {txn_hash}")
            
            await self.rest_client.wait_for_transaction(txn_hash)
            logger.info(f"交易已确认: {txn_hash}")
            
            return txn_hash

        except Exception as e:
            logger.error("转账失败:")
            logger.error(f"- 错误类型: {type(e).__name__}")
            logger.error(f"- 错误信息: {str(e)}")
            logger.error("- 堆栈跟踪:")
            logger.error(traceback.format_exc())
            raise

    async def grab_red_packet(self, recv):
        """抢红包"""
        grabber = recv["sender"]
        content = recv["content"]

        if len(content) < 2:
            self.send_message(recv, "❌参数不足! 格式:\n/抢红包 验证码 [可选:钱包地址]")
            return

        captcha = content[1]
        wallet_address = content[2] if len(content) > 2 else None
       
      
        # 验证红包
        if captcha not in self.red_packets:
            self.send_message(recv, "❌红包不存在或已过期!")
            return

        packet = self.red_packets[captcha]
        
        # 添加时间检查的详细日志
        current_time = time.time()
        packet_time = packet["timestamp"]
        time_diff = current_time - packet_time
        
        logger.info(f"红包时间检查:\n- 当前时间: {datetime.fromtimestamp(current_time)}\n- 红包创建时间: {datetime.fromtimestamp(packet_time)}\n- 时间差: {time_diff} 秒\n- 超时阈值: {self.max_time} 秒")
      
        # 验证状态
        if grabber in packet["claimed"]:
            self.send_message(recv, "❌您已经抢过这个红包了!")
            return
        if not packet["amounts"]:
            self.send_message(recv, "❌红包已被抢完!")
            return
        if time_diff > self.max_time:
            logger.warning(f"红包超时: 时间差 {time_diff} 秒 > 阈值 {self.max_time} 秒")
            self.send_message(recv, "❌红包已过期!")
            return
    

    @staticmethod
    def generate_captcha(length=4):
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
    
    async def expired_aptos_airdrop_check(self):
        """检查过期红包"""
        try:
            current_time = time.time()
            logger.info(f"开始检查过期红包 - 当前时间: {datetime.fromtimestamp(current_time)}")
            
            for code in list(self.red_packets.keys()):
                packet = self.red_packets[code]
                packet_time = packet["timestamp"]
                time_diff = current_time - packet_time
                
                logger.info(f"检查红包 {code}:")
                logger.info(f"- 创建时间: {datetime.fromtimestamp(packet_time)}")
                logger.info(f"- 存在时间: {time_diff} 秒")
                
                if time_diff > self.max_time:
                    logger.info(f"发现超时红包 {code}:")
                    logger.info(f"- 超时时间: {time_diff - self.max_time} 秒")
                    
                    if packet["amounts"]:
                        total_remaining_octas = sum(packet["amounts"])
                        total_remaining_apt = total_remaining_octas / 100_000_000
                        
                        try:
                            logger.info(f"准备退还红包:")
                            logger.info(f"- 金额: {total_remaining_apt} APT")
                            logger.info(f"- 接收地址: {packet['sender_address']}")
                            
                            sender_address_obj = AccountAddress.from_str(packet['sender_address'])
                            txn_hash = await self.transfer_apt(
                                self.bot_account,
                                sender_address_obj,
                                total_remaining_octas
                            )
                            
                            message = f"""
    📢 红包 {code} 已过期
    💰 剩余 {total_remaining_apt:.8f} APT 已退回给发送者
    🔗 交易hash: {txn_hash}
                            """
                            self.bot.send_text_msg(packet["room"], message)
                            logger.info(f"退还成功: {txn_hash}")
                        except Exception as e:
                            logger.error(f"退还红包失败:")
                            logger.error(f"- 错误类型: {type(e).__name__}")
                            logger.error(f"- 错误信息: {str(e)}")
                            logger.error(traceback.format_exc())
                    
                    # 删除超时红包
                    del self.red_packets[code]
                    logger.info(f"已删除超时红包: {code}")
                    
        except Exception as e:
            logger.error("检查超时红包时发生错误:")
            logger.error(f"- 错误类型: {type(e).__name__}")
            logger.error(f"- 错误信息: {str(e)}")
            logger.error(traceback.format_exc())