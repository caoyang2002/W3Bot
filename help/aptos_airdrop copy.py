# import yaml
# import os
# import random
# import time
# from pathlib import Path
# import asyncio
# from loguru import logger
# import pywxdll
# from utils.plugin_interface import PluginInterface
# from sdk.aptos_python.async_client import RestClient
# from sdk.aptos_python.account import Account
# from sdk.aptos_python.account_address import AccountAddress
# from typing import Tuple, Union, Optional, Dict, List
# from dataclasses import dataclass
# from utils.singleton import singleton
# from utils.aptos_user_database import AptosUserDatabase
# from captcha.image import ImageCaptcha

# @dataclass
# class RedPacketInfo:
#     """红包信息"""
#     total_amount: float
#     amount: int
#     sender: str
#     amount_list: List[float]
#     claimed: List[Tuple[str, str]]
#     created_time: float
#     chatroom: str
#     sender_nick: str

# class aptos_airdrop(PluginInterface):
#     def __init__(self):
#         # 加载插件配置
#         config_path = "plugins/aptos_airdrop.yml"
#         with open(config_path, "r", encoding="utf-8") as f:
#             self.plugin_config = yaml.safe_load(f.read())

#         # 网络配置
#         self.networks = {
#             "testnet": {
#                 "node_url": self.plugin_config.get("testnet_node_url", "https://fullnode.testnet.aptoslabs.com/v1"),
#                 "explorer_url": self.plugin_config.get("testnet_explorer_url", "https://explorer.aptoslabs.com")
#             },
#             "mainnet": {
#                 "node_url": self.plugin_config.get("mainnet_node_url", "https://fullnode.mainnet.aptoslabs.com/v1"),
#                 "explorer_url": self.plugin_config.get("mainnet_explorer_url", "https://explorer.aptoslabs.com")
#             }
#         }

#         # 默认使用 testnet
#         self.current_network = "testnet"
#         self.set_network(self.current_network)

#         # 加载主配置
#         self.config = self.load_config()
#         self.bot = pywxdll.Pywxdll(self.config["ip"], self.config["port"])
        
#         # 初始化合约账户
#         self.contract_account = Account.load_key(self.config["aptos_private_key"])
        
#         # 初始化数据库和红包存储
#         self.user_db = AptosUserDatabase()
#         self.red_packets: Dict[str, RedPacketInfo] = {}
        
#         # 确保缓存目录存在
#         self._ensure_cache_directory()

#     def set_network(self, network: str):
#         """设置当前网络"""
#         network = network.lower()
#         if network not in self.networks:
#             raise ValueError(f"不支持的网络: {network}")
        
#         self.current_network = network
#         network_config = self.networks[network]
#         self.rest_client = RestClient(network_config["node_url"])

#     def load_config(self):
#         """加载主配置文件"""
#         try:
#             with open("main_config.yml", "r", encoding="utf-8") as f:
#                 return yaml.safe_load(f.read())
#         except Exception as e:
#             logger.error(f"加载配置文件失败: {e}")
#             raise

#     def parse_claim_command(self, content: list) -> Tuple[str, Optional[str]]:
#         """
#         解析领取红包命令参数
#         返回: (captcha, address可选)
#         """
#         try:
#             args = [arg for arg in content[1:] if arg.strip()]
#             if not args:
#                 raise ValueError("缺少验证码")

#             captcha = args[0]
#             address = args[1] if len(args) > 1 else None

#             if address and not address.startswith("0x"):
#                 raise ValueError("地址必须以 0x 开头")

#             return captcha, address

#         except ValueError as e:
#             raise ValueError(f"命令解析错误: {str(e)}")
        
#     async def run(self, recv):
#         try:
#             content = [item for item in recv["content"] if item.strip()]
#             logger.info(f"收到命令: {content}")
            
#             if not content:
#                 return await self.send_help(recv)

#             command = content[0].lower()
            
#             # 检查是否是帮助命令
#             if len(content) > 1 and content[1] in ["帮助", "help", "查看帮助"]:
#                 return await self.send_help(recv)
            
#             if command in ["/redpack", "/发红包", "/airdrop"]:
#                 await self._handle_send_packet(recv)
#             elif command in ["/claim", "/抢红包", "/领取"]:
#                 await self._handle_claim_packet(recv)
#             else:
#                 await self.send_help(recv)

#         except ValueError as e:
#             await self.send_error(recv, str(e))
#         except Exception as e:
#             logger.error(f"处理命令时发生错误: {e}")
#             await self.send_error(recv, f"处理命令失败: {e}")

#     def parse_send_command(self, content: list) -> Tuple[float, int]:
#         """解析发红包命令参数"""
#         try:
#             if content[1] in ["帮助", "help", "查看帮助"]:
#                 raise ValueError("显示帮助信息")

#             args = [arg for arg in content[1:] if arg.strip()]
#             if len(args) != 2:
#                 raise ValueError(
#                     "参数格式错误\n"
#                     "正确格式：/redpack <APT数量> <红包个数>\n"
#                     "例如：/redpack 10 5"
#                 )

#             try:
#                 total_amount = float(args[0])
#             except ValueError:
#                 raise ValueError(
#                     "APT数量必须是数字\n"
#                     f"有效范围：{self.plugin_config['min_amount']} - {self.plugin_config['max_amount']} APT"
#                 )

#             try:
#                 packet_count = int(args[1])
#             except ValueError:
#                 raise ValueError(
#                     "红包个数必须是整数\n"
#                     f"有效范围：1 - {self.plugin_config['max_packet']} 个"
#                 )

#             if not (self.plugin_config["min_amount"] <= total_amount <= self.plugin_config["max_amount"]):
#                 raise ValueError(
#                     f"APT数量超出范围\n"
#                     f"最小：{self.plugin_config['min_amount']} APT\n"
#                     f"最大：{self.plugin_config['max_amount']} APT"
#                 )

#             if not (1 <= packet_count <= self.plugin_config["max_packet"]):
#                 raise ValueError(
#                     f"红包个数超出范围\n"
#                     f"最小：1个\n"
#                     f"最大：{self.plugin_config['max_packet']}个"
#                 )

#             per_amount = total_amount / packet_count
#             if per_amount < self.plugin_config["min_per_packet"]:
#                 raise ValueError(
#                     f"单个红包金额太小\n"
#                     f"当前：{per_amount:.6f} APT\n"
#                     f"最小：{self.plugin_config['min_per_packet']} APT"
#                 )

#             return total_amount, packet_count

#         except ValueError as e:
#             raise ValueError(str(e))

#     async def send_help(self, recv):
#         """发送帮助信息"""
#         help_message = (
#             f"\n🎁 Aptos链上红包/空投系统\n"
#             f"━━━━━━━━━━━━━━━\n"
#             f"📢 功能介绍：\n"
#             f"在群内发送APT代币红包，支持随机金额分配\n"
#             f"可保存钱包地址，方便多次领取\n\n"
#             f"📝 发红包命令：\n"
#             f"• /redpack <APT数量> <红包个数>\n"
#             f"• /发红包 <APT数量> <红包个数>\n"
#             f"• /airdrop <APT数量> <红包个数>\n\n"
#             f"🎯 抢红包命令：\n"
#             f"• /claim <验证码> [钱包地址]\n"
#             f"• /抢红包 <验证码> [钱包地址]\n"
#             f"• /领取 <验证码> [钱包地址]\n\n"
#             f"📋 参数说明:\n"
#             f"• APT数量: {self.plugin_config['min_amount']} - {self.plugin_config['max_amount']} APT\n"
#             f"• 红包个数: 1 - {self.plugin_config['max_packet']} 个\n"
#             f"• 最小单个金额: {self.plugin_config['min_per_packet']} APT\n"
#             f"• 红包有效期: {self.plugin_config['max_time']}秒\n"
#             f"• 钱包地址: 可选参数，不填则使用历史地址\n\n"
#             f"💡 使用示例:\n"
#             f"1️⃣ 发送红包：\n"
#             f"   /redpack 10 5  (发10 APT分5个红包)\n\n"
#             f"2️⃣ 领取红包：\n"
#             f"   /claim abc12  (使用保存的地址)\n"
#             f"   /claim abc12 0x123...  (使用新地址)\n"
#             f"━━━━━━━━━━━━━━━"
#         )
#         await self.send_message(recv, help_message)

#     async def send_error(self, recv, message):
#         """发送错误消息"""
#         error_msg = (
#             f"\n❌ 操作失败\n"
#             f"━━━━━━━━━━━━━━━\n"
#             f"📛 错误信息：\n{message}\n"
#             f"━━━━━━━━━━━━━━━\n"
#             f"💡 发送 /redpack help 查看完整帮助"
#         )
#         await self.send_message(recv, error_msg, "error")


#     async def _handle_send_packet(self, recv):
#         """处理发送红包命令"""
#         try:
#             # 解析命令
#             total_amount, packet_count = self.parse_send_command(recv["content"])
            
#             # 检查发送者账户余额
#             try:
#                 balance = await self.rest_client.account_balance(self.contract_account.address())
#                 if balance < total_amount * 100_000_000:
#                     await self.send_error(recv, (
#                         "合约账户余额不足\n"
#                         f"需要: {total_amount:.4f} APT\n"
#                         f"当前: {balance/100_000_000:.4f} APT"
#                     ))
#                     return
#             except Exception as e:
#                 logger.error(f"检查余额失败: {e}")
#                 await self.send_error(recv, "检查余额失败，请稍后重试")
#                 return
                
#             # 生成红包信息
#             captcha, image_path = self._generate_captcha()
#             amount_list = self._split_amount(total_amount, packet_count)
            
#             red_packet = RedPacketInfo(
#                 total_amount=total_amount,
#                 amount=packet_count,
#                 sender=recv["sender"],
#                 amount_list=amount_list,
#                 claimed=[],
#                 created_time=time.time(),
#                 chatroom=recv["from"],
#                 sender_nick=self.bot.get_contact_profile(recv["sender"])["nickname"]
#             )
            
#             self.red_packets[captcha] = red_packet
            
#             # 发送红包消息
#             await self._send_redpacket_message(recv, red_packet, captcha, image_path)
            
#         except Exception as e:
#             logger.error(f"发送红包失败: {e}")
#             await self.send_error(recv, str(e))

#     async def _handle_claim_packet(self, recv):
#         """处理领取红包命令"""
#         try:
#             # 解析命令
#             captcha, address = self.parse_claim_command(recv["content"])
            
#             # 获取用户数据
#             user_data = self.user_db.get_user_data(recv["sender"])
            
#             # 处理地址逻辑
#             if not address and (not user_data or not user_data.get('WALLET_ADDRESS')):
#                 await self.send_error(recv, "请提供钱包地址或先绑定地址")
#                 return
            
#             if not address:
#                 address = user_data['WALLET_ADDRESS']
#                 await self.send_message(recv, f"\n📝 使用已保存的地址: {self.format_address(address)}")

#             # 验证红包
#             error = self._validate_claim(recv, captcha, address)
#             if error:
#                 await self.send_error(recv, error)
#                 return
                
#             # 处理领取逻辑
#             red_packet = self.red_packets[captcha]
#             apt_amount = red_packet.amount_list.pop()
            
#             # 更新用户地址
#             self.user_db.add_or_update_user({
#                 'wxid': recv["sender"],
#                 'wallet_address': address,
#                 'nickname': self.bot.get_contact_profile(recv["sender"])["nickname"]
#             })

#             try:
#                 # 转换地址格式
#                 receipt_address = AccountAddress.from_hex(address)
                
#                 # 执行转账
#                 txn_hash = await self.rest_client.bcs_transfer(
#                     self.contract_account,
#                     receipt_address,
#                     int(apt_amount * 100_000_000)
#                 )
#                 await self.rest_client.wait_for_transaction(txn_hash)
                
#                 # 记录领取
#                 red_packet.claimed.append((recv["sender"], address))
                
#                 # 发送成功消息
#                 await self._send_claim_success(recv, address, apt_amount, txn_hash, red_packet)
                
#             except Exception as e:
#                 logger.error(f"转账失败: {e}")
#                 # 恢复未领取的金额
#                 red_packet.amount_list.append(apt_amount)
#                 await self.send_error(recv, f"转账失败: {str(e)}\n请检查地址是否正确")
                
#         except Exception as e:
#             logger.error(f"领取红包失败: {e}")
#             await self.send_error(recv, str(e))

#     async def _send_claim_success(self, recv: dict, address: str, amount: float, txn_hash: str, red_packet: RedPacketInfo):
#         """发送领取成功消息"""
#         try:
#             # 获取领取者昵称
#             claimer_nick = self.bot.get_contact_profile(recv["sender"])["nickname"]
            
#             # 构建成功消息
#             success_msg = (
#                 f"\n🎉 恭喜 {claimer_nick} 抢到了 {amount:.4f} APT！\n"
#                 f"━━━━━━━━━━━━━━━\n"
#                 f"💰 转入地址: {self.format_address(address)}\n"
#                 f"📜 交易Hash: {self.format_address(txn_hash)}\n"
#                 f"🔍 浏览器: {self.networks[self.current_network]['explorer_url']}/txn/{txn_hash}"
#             )
#             await self.send_message(recv, success_msg)
            
#             # 如果红包已抢完，发送汇总信息
#             if not red_packet.amount_list:
#                 claimed_addresses = [addr for _, addr in red_packet.claimed]
#                 unique_addresses = len(set(claimed_addresses))
                
#                 summary_msg = (
#                     f"\n🎊 红包已抢完！\n"
#                     f"━━━━━━━━━━━━━━━\n"
#                     f"💁 发送者: {red_packet.sender_nick}\n"
#                     f"💰 总金额: {red_packet.total_amount:.4f} APT\n"
#                     f"👥 红包个数: {red_packet.amount}个\n"
#                     f"📍 参与人数: {len(red_packet.claimed)}人\n"
#                     f"🎯 不同地址: {unique_addresses}个\n"
#                     f"⏱️ 总耗时: {(time.time() - red_packet.created_time):.1f}秒"
#                 )
#                 await self.send_message(recv, summary_msg)
                
#         except Exception as e:
#             logger.error(f"发送领取成功消息失败: {e}")
#             raise

#     def _validate_claim(self, recv: dict, captcha: str, address: str) -> Optional[str]:
#         """验证领取红包请求"""
#         if captcha not in self.red_packets:
#             return (
#                 "验证码错误或红包不存在\n"
#                 "请检查验证码是否输入正确"
#             )
            
#         red_packet = self.red_packets[captcha]
        
#         if not red_packet.amount_list:
#             return "红包已被抢完\n请等待下一个红包"
            
#         if recv['fromType'] == 'friend':
#             return "红包只能在群里抢\n请在群聊中使用此命令"
            
#         if any(wxid == recv["sender"] for wxid, _ in red_packet.claimed):
#             return "你已经抢过这个红包了\n每人限领一次"
            
#         if recv["sender"] == red_packet.sender:
#             return "不能抢自己的红包\n请等待其他红包"
        
#         try:
#             # 验证地址格式
#             addr = address.strip()
#             if not addr.startswith('0x'):
#                 return (
#                     "无效的Aptos地址\n"
#                     "地址必须以0x开头"
#                 )
            
#             # 尝试转换地址格式
#             AccountAddress.from_hex(addr)
            
#         except Exception as e:
#             return (
#                 "无效的Aptos地址\n"
#                 "地址格式：0x + 64位十六进制字符\n"
#                 f"错误信息：{str(e)}"
#             )
            
#         # 检查红包是否超时
#         if time.time() - red_packet.created_time > self.plugin_config["max_time"]:
#             del self.red_packets[captcha]
#             return (
#                 "红包已过期\n"
#                 f"红包有效期为{self.plugin_config['max_time']}秒"
#             )
            
#         return None
    
#     async def send_message(self, recv, message, log_level="info"):
#         """发送消息"""
#         getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
#         self.bot.send_text_msg(recv["from"], message)

#     @staticmethod
#     def _ensure_cache_directory() -> None:
#         """确保缓存目录存在"""
#         cache_path = Path("resources/cache")
#         if not cache_path.exists():
#             logger.info("创建cache文件夹")
#             cache_path.mkdir(parents=True, exist_ok=True)

#     @staticmethod
#     def format_address(address: str, length: int = 6) -> str:
#         """格式化地址显示"""
#         if len(address) <= length * 2:
#             return address
#         return f"{address[:length]}...{address[-length:]}"

#     @staticmethod
#     def _generate_captcha() -> Tuple[str, str]:
#         """生成验证码和图片"""
#         chars = "abdfghkmnpqtwxy2346789"
#         captcha = ''.join(random.sample(chars, 5))
        
#         image = ImageCaptcha().generate_image(captcha)
#         path = f"resources/cache/{captcha}.jpg"
#         image.save(path)
        
#         return captcha, os.path.abspath(path)

#     def _split_amount(self, total: float, count: int) -> List[float]:
#         """随机分配红包金额"""
#         # 转换为最小单位(0.000001 APT)进行计算
#         min_unit = self.plugin_config["min_per_packet"]
#         total_units = int(total / min_unit)
#         count_units = int(count)
        
#         if total_units < count_units:
#             raise ValueError("红包总金额不能小于红包个数")
            
#         # 确保每个红包至少有一个最小单位
#         amounts = [1] * count_units
#         remaining_units = total_units - count_units
        
#         # 随机分配剩余金额
#         while remaining_units > 0:
#             for i in range(count_units):
#                 if remaining_units <= 0:
#                     break
#                 rand_amount = random.randint(0, remaining_units)
#                 amounts[i] += rand_amount
#                 remaining_units -= rand_amount
        
#         # 转换回APT
#         return [amount * min_unit for amount in amounts]

#     async def _send_redpacket_message(self, recv: dict, red_packet: RedPacketInfo, captcha: str, image_path: str):
#         """发送红包消息"""
#         try:
#             # 发送验证码图片
#             self.bot.send_image_msg(recv["from"], image_path)
            
#             # 构建红包消息
#             message = (
#                 f"\n🧧 收到一个APT红包\n"
#                 f"━━━━━━━━━━━━━━━\n"
#                 f"👤 发送者: {red_packet.sender_nick}\n"
#                 f"💰 金额: {red_packet.total_amount:.4f} APT\n"
#                 f"📦 数量: {red_packet.amount}个\n"
#                 f"🎯 口令: {captcha}\n"
#                 f"━━━━━━━━━━━━━━━\n"
#                 f"📝 使用以下命令领取:\n"
#                 f"/claim {captcha} <钱包地址>\n"
#                 f"或\n"
#                 f"/抢红包 {captcha} <钱包地址>\n"
#                 f"提示: 不填地址则使用上次地址"
#             )
#             await self.send_message(recv, message)
            
#             # 设置红包过期检查
#             asyncio.create_task(self._check_expiry(captcha, recv["from"]))
            
#         except Exception as e:
#             logger.error(f"发送红包消息失败: {e}")
#             raise

#     async def _check_expiry(self, captcha: str, chat_room: str):
#         """检查红包是否过期"""
#         try:
#             await asyncio.sleep(self.plugin_config["max_time"])
            
#             # 检查红包是否还存在且未被领完
#             if captcha in self.red_packets and self.red_packets[captcha].amount_list:
#                 red_packet = self.red_packets[captcha]
                
#                 # 计算未领取金额
#                 remaining_amount = sum(red_packet.amount_list)
                
#                 # 发送过期消息
#                 expire_msg = (
#                     f"\n⏰ 红包已过期\n"
#                     f"━━━━━━━━━━━━━━━\n"
#                     f"👤 发送者: {red_packet.sender_nick}\n"
#                     f"💰 未领取: {remaining_amount:.4f} APT\n"
#                     f"📦 未领取数量: {len(red_packet.amount_list)}个"
#                 )
                
#                 # 发送消息到群
#                 self.bot.send_text_msg(chat_room, expire_msg)
                
#                 # 从红包列表中移除
#                 del self.red_packets[captcha]
                
#         except Exception as e:
#             logger.error(f"检查红包过期失败: {e}")

#     async def _check_all_expired(self):
#         """定期检查所有过期红包"""
#         while True:
#             try:
#                 current_time = time.time()
#                 expired_packets = []
                
#                 for captcha, red_packet in self.red_packets.items():
#                     if current_time - red_packet.created_time > self.plugin_config["max_time"]:
#                         expired_packets.append((captcha, red_packet))
                
#                 for captcha, red_packet in expired_packets:
#                     if red_packet.amount_list:  # 如果还有未领取的金额
#                         expire_msg = (
#                             f"\n⏰ 红包已过期\n"
#                             f"━━━━━━━━━━━━━━━\n"
#                             f"👤 发送者: {red_packet.sender_nick}\n"
#                             f"💰 未领取: {sum(red_packet.amount_list):.4f} APT\n"
#                             f"📦 未领取数量: {len(red_packet.amount_list)}个"
#                         )
#                         self.bot.send_text_msg(red_packet.chatroom, expire_msg)
                    
#                     del self.red_packets[captcha]
                    
#             except Exception as e:
#                 logger.error(f"检查过期红包时发生错误: {e}")
                
#             await asyncio.sleep(60)  # 每分钟检查一次

#     def __del__(self):
#         """清理资源"""
#         try:
#             # 关闭数据库连接
#             self.user_db.__del__()
#         except Exception as e:
#             logger.error(f"清理资源时发生错误: {e}")



import yaml
import os
import random
import time
from pathlib import Path
import asyncio
from loguru import logger
import pywxdll
from utils.plugin_interface import PluginInterface
from sdk.aptos_python.async_client import RestClient
from sdk.aptos_python.account import Account
from sdk.aptos_python.account_address import AccountAddress
from typing import Tuple, Union, Optional, Dict, List
from dataclasses import dataclass
from utils.singleton import singleton
from utils.aptos_user_database import AptosUserDatabase
from captcha.image import ImageCaptcha

@dataclass
class RedPacketInfo:
    """红包信息"""
    total_amount: float           # 总金额
    amount: int                   # 红包数量
    sender: str                   # 发送者wxid
    amount_list: List[float]      # 金额列表
    claimed: List[Tuple[str, str]]  # 已领取列表 (wxid, 钱包地址)
    created_time: float          # 创建时间
    chatroom: str                # 群聊ID
    sender_nick: str             # 发送者昵称

# class aptos_airdrop(PluginInterface):
#     def __init__(self):
#         try:
#             # 加载插件配置
#             config_path = "plugins/aptos_airdrop.yml"
#             with open(config_path, "r", encoding="utf-8") as f:
#                 self.plugin_config = yaml.safe_load(f.read())

#             # 网络配置
#             self.networks = {
#                 "testnet": {
#                     "node_url": self.plugin_config.get("testnet_node_url", "https://fullnode.testnet.aptoslabs.com/v1"),
#                     "explorer_url": self.plugin_config.get("testnet_explorer_url", "https://explorer.aptoslabs.com")
#                 },
#                 "mainnet": {
#                     "node_url": self.plugin_config.get("mainnet_node_url", "https://fullnode.mainnet.aptoslabs.com/v1"),
#                     "explorer_url": self.plugin_config.get("mainnet_explorer_url", "https://explorer.aptoslabs.com")
#                 }
#             }

#             # 默认使用 testnet
#             self.current_network = "testnet"
#             self.set_network(self.current_network)

#             # 加载主配置
#             self.config = self.load_config()
#             self.bot = pywxdll.Pywxdll(self.config["ip"], self.config["port"])
            
#             # 初始化合约账户
#             self.contract_account = Account.load_key(self.config["aptos_private_key"])
            
#             # 初始化数据库和红包存储
#             self._init_database()
#             self.red_packets: Dict[str, RedPacketInfo] = {}
            
#             # 确保缓存目录存在
#             self._ensure_cache_directory()

#             # 初始化定时任务
#             self.expiry_tasks = set()
#             self.check_all_expired_task = None

#             logger.info("Aptos红包插件初始化成功")
            
#         except Exception as e:
#             logger.error(f"初始化插件失败: {e}")
#             raise

#     def _init_database(self):
#         """初始化数据库连接"""
#         try:
#             self.user_db = AptosUserDatabase()
#         except Exception as e:
#             logger.error(f"初始化数据库失败: {e}")
#             raise

#     async def start(self):
#         """启动插件的异步任务"""
#         if self.check_all_expired_task is None:
#             self.check_all_expired_task = asyncio.create_task(self._check_all_expired())
#             logger.info("启动红包过期检查任务")

#     async def stop(self):
#         """停止所有异步任务"""
#         # 取消所有过期检查任务
#         for task in self.expiry_tasks:
#             if not task.done():
#                 task.cancel()
#         self.expiry_tasks.clear()

#         # 取消主过期检查任务
#         if self.check_all_expired_task and not self.check_all_expired_task.done():
#             self.check_all_expired_task.cancel()
#             try:
#                 await self.check_all_expired_task
#             except asyncio.CancelledError:
#                 pass
#         self.check_all_expired_task = None
        
#         logger.info("停止所有红包过期检查任务")

#     def set_network(self, network: str):
#         """设置当前网络"""
#         network = network.lower()
#         if network not in self.networks:
#             raise ValueError(f"不支持的网络: {network}")
        
#         self.current_network = network
#         network_config = self.networks[network]
#         self.rest_client = RestClient(network_config["node_url"])

#     def load_config(self):
#         """加载主配置文件"""
#         try:
#             with open("main_config.yml", "r", encoding="utf-8") as f:
#                 return yaml.safe_load(f.read())
#         except Exception as e:
#             logger.error(f"加载配置文件失败: {e}")
#             raise

#     def parse_send_command(self, content: list) -> Tuple[float, int]:
#         """解析发红包命令"""
#         try:
#             if content[1] in ["帮助", "help", "查看帮助"]:
#                 raise ValueError("显示帮助信息")

#             args = [arg for arg in content[1:] if arg.strip()]
#             if len(args) != 2:
#                 raise ValueError(
#                     "参数格式错误\n"
#                     "正确格式：/redpack <APT数量> <红包个数>\n"
#                     "例如：/redpack 10 5"
#                 )

#             try:
#                 total_amount = float(args[0])
#             except ValueError:
#                 raise ValueError(
#                     "APT数量必须是数字\n"
#                     f"有效范围：{self.plugin_config['min_amount']} - {self.plugin_config['max_amount']} APT"
#                 )

#             try:
#                 packet_count = int(args[1])
#             except ValueError:
#                 raise ValueError(
#                     "红包个数必须是整数\n"
#                     f"有效范围：1 - {self.plugin_config['max_packet']} 个"
#                 )

#             if not (self.plugin_config["min_amount"] <= total_amount <= self.plugin_config["max_amount"]):
#                 raise ValueError(
#                     f"APT数量超出范围\n"
#                     f"最小：{self.plugin_config['min_amount']} APT\n"
#                     f"最大：{self.plugin_config['max_amount']} APT"
#                 )

#             if not (1 <= packet_count <= self.plugin_config["max_packet"]):
#                 raise ValueError(
#                     f"红包个数超出范围\n"
#                     f"最小：1个\n"
#                     f"最大：{self.plugin_config['max_packet']}个"
#                 )

#             per_amount = total_amount / packet_count
#             if per_amount < self.plugin_config["min_per_packet"]:
#                 raise ValueError(
#                     f"单个红包金额太小\n"
#                     f"当前：{per_amount:.6f} APT\n"
#                     f"最小：{self.plugin_config['min_per_packet']} APT"
#                 )

#             return total_amount, packet_count

#         except ValueError as e:
#             raise ValueError(str(e))

#     def parse_claim_command(self, content: list) -> Tuple[str, Optional[str]]:
#         """解析领取红包命令"""
#         try:
#             args = [arg for arg in content[1:] if arg.strip()]
#             if not args:
#                 raise ValueError("缺少验证码")

#             captcha = args[0]
#             address = args[1] if len(args) > 1 else None

#             if address and not address.startswith("0x"):
#                 raise ValueError("地址必须以 0x 开头")

#             return captcha, address

#         except ValueError as e:
#             raise ValueError(f"命令解析错误: {str(e)}")

#     async def _handle_send_packet(self, recv):
#         """处理发送红包命令"""
#         try:
#             # 解析命令
#             total_amount, packet_count = self.parse_send_command(recv["content"])
            
#             # 检查发送者账户余额
#             try:
#                 balance = await self.rest_client.account_balance(self.contract_account.address())
#                 if balance < total_amount * 100_000_000:
#                     await self.send_error(recv, (
#                         "合约账户余额不足\n"
#                         f"需要: {total_amount:.4f} APT\n"
#                         f"当前: {balance/100_000_000:.4f} APT"
#                     ))
#                     return
#             except Exception as e:
#                 logger.error(f"检查余额失败: {e}")
#                 await self.send_error(recv, "检查余额失败，请稍后重试")
#                 return
                
#             # 生成红包信息
#             captcha, image_path = self._generate_captcha()
#             amount_list = self._split_amount(total_amount, packet_count)
            
#             red_packet = RedPacketInfo(
#                 total_amount=total_amount,
#                 amount=packet_count,
#                 sender=recv["sender"],
#                 amount_list=amount_list,
#                 claimed=[],
#                 created_time=time.time(),
#                 chatroom=recv["from"],
#                 sender_nick=self.bot.get_contact_profile(recv["sender"])["nickname"]
#             )
            
#             self.red_packets[captcha] = red_packet
            
#             # 发送红包消息
#             await self._send_redpacket_message(recv, red_packet, captcha, image_path)
            
#         except Exception as e:
#             logger.error(f"发送红包失败: {e}")
#             await self.send_error(recv, str(e))

#     def is_valid_captcha(self, captcha: str) -> bool:
#         """验证码格式检查"""
#         if not captcha:
#             return False
#         # 验证码必须是5位字母数字组合
#         if len(captcha) != 5:
#             return False
#         # 验证码只能包含指定字符
#         valid_chars = set("abdfghkmnpqtwxy2346789")
#         return all(c in valid_chars for c in captcha.lower())

#     def _cleanup_redpacket(self, captcha: str):
#         """清理红包资源"""
#         try:
#             # 删除验证码图片
#             image_path = f"resources/cache/{captcha}.jpg"
#             if os.path.exists(image_path):
#                 os.remove(image_path)
            
#             # 删除红包记录
#             if captcha in self.red_packets:
#                 del self.red_packets[captcha]
                
#             logger.info(f"清理红包资源完成: {captcha}")
#         except Exception as e:
#             logger.error(f"清理红包资源失败: {e}")

#     async def _check_expiry(self, captcha: str, chat_room: str):
#         """检查红包是否过期"""
#         try:
#             await asyncio.sleep(self.plugin_config["max_time"])
            
#             if captcha in self.red_packets:
#                 red_packet = self.red_packets[captcha]
                
#                 if red_packet.amount_list:  # 如果还有未领取的金额
#                     remaining_amount = sum(red_packet.amount_list)
#                     expire_msg = (
#                         f"\n⏰ 红包已过期\n"
#                         f"━━━━━━━━━━━━━━━\n"
#                         f"👤 发送者: {red_packet.sender_nick}\n"
#                         f"💰 未领取: {remaining_amount:.4f} APT\n"
#                         f"📦 未领取数量: {len(red_packet.amount_list)}个"
#                     )
#                     self.bot.send_text_msg(chat_room, expire_msg)
                
#                 # 清理资源
#                 self._cleanup_redpacket(captcha)
                
#         except asyncio.CancelledError:
#             logger.info(f"红包 {captcha} 的过期检查任务被取消")
#         except Exception as e:
#             logger.error(f"检查红包过期失败: {e}")

#     def _validate_claim(self, recv: dict, red_packet: RedPacketInfo, address: str) -> Optional[str]:
#         """验证领取红包请求"""
#         if not red_packet.amount_list:
#             return "红包已被抢完\n请等待下一个红包"
            
#         if recv['fromType'] == 'friend':
#             return "红包只能在群里抢\n请在群聊中使用此命令"
            
#         if any(wxid == recv["sender"] for wxid, _ in red_packet.claimed):
#             return "你已经抢过这个红包了\n每人限领一次"
            
#         if recv["sender"] == red_packet.sender:
#             return "不能抢自己的红包\n请等待其他红包"
        
#         try:
#             # 验证地址格式
#             addr = address.strip()
#             if not addr.startswith('0x'):
#                 return (
#                     "无效的Aptos地址\n"
#                     "地址必须以0x开头"
#                 )
            
#             # 尝试转换地址格式
#             AccountAddress.from_hex(addr)
            
#         except Exception as e:
#             return (
#                 "无效的Aptos地址\n"
#                 "地址格式：0x + 64位十六进制字符\n"
#                 f"错误信息：{str(e)}"
#             )
            
#         # 检查红包是否超时
#         if time.time() - red_packet.created_time > self.plugin_config["max_time"]:
#             return (
#                 "红包已过期\n"
#                 f"红包有效期为{self.plugin_config['max_time']}秒"
#             )
            
#         return None

#     async def _send_claim_success(self, recv: dict, address: str, amount: float, txn_hash: str, red_packet: RedPacketInfo):
#         """发送领取成功消息"""
#         try:
#             # 获取领取者昵称
#             claimer_nick = self.bot.get_contact_profile(recv["sender"])["nickname"]
            
#             # 构建成功消息
#             success_msg = (
#                 f"\n🎉 恭喜 {claimer_nick} 抢到了 {amount:.4f} APT！\n"
#                 f"━━━━━━━━━━━━━━━\n"
#                 f"💰 转入地址: {self.format_address(address)}\n"
#                 f"📜 交易Hash: {self.format_address(txn_hash)}\n"
#                 f"🔍 浏览器: {self.networks[self.current_network]['explorer_url']}/txn/{txn_hash}"
#             )
#             await self.send_message(recv, success_msg)
            
#             # 如果红包已抢完，发送汇总信息
#             if not red_packet.amount_list:
#                 claimed_addresses = [addr for _, addr in red_packet.claimed]
#                 unique_addresses = len(set(claimed_addresses))
                
#                 summary_msg = (
#                     f"\n🎊 红包已抢完！\n"
#                     f"━━━━━━━━━━━━━━━\n"
#                     f"💁 发送者: {red_packet.sender_nick}\n"
#                     f"💰 总金额: {red_packet.total_amount:.4f} APT\n"
#                     f"👥 红包个数: {red_packet.amount}个\n"
#                     f"📍 参与人数: {len(red_packet.claimed)}人\n"
#                     f"🎯 不同地址: {unique_addresses}个\n"
#                     f"⏱️ 总耗时: {(time.time() - red_packet.created_time):.1f}秒"
#                 )
#                 await self.send_message(recv, summary_msg)
                
#                 # 删除红包记录
#                 if captcha in self.red_packets:
#                     del self.red_packets[captcha]
                
#         except Exception as e:
#             logger.error(f"发送领取成功消息失败: {e}")
#             raise

#     def _validate_claim(self, recv: dict, captcha: str, address: str) -> Optional[str]:
#         """验证领取红包请求"""
#         if captcha not in self.red_packets:
#             return (
#                 "验证码错误或红包不存在\n"
#                 "请检查验证码是否输入正确"
#             )
            
#         red_packet = self.red_packets[captcha]
        
#         if not red_packet.amount_list:
#             return "红包已被抢完\n请等待下一个红包"
            
#         if recv['fromType'] == 'friend':
#             return "红包只能在群里抢\n请在群聊中使用此命令"
            
#         if any(wxid == recv["sender"] for wxid, _ in red_packet.claimed):
#             return "你已经抢过这个红包了\n每人限领一次"
            
#         if recv["sender"] == red_packet.sender:
#             return "不能抢自己的红包\n请等待其他红包"
        
#         try:
#             # 验证地址格式
#             addr = address.strip()
#             if not addr.startswith('0x'):
#                 return (
#                     "无效的Aptos地址\n"
#                     "地址必须以0x开头"
#                 )
            
#             # 尝试转换地址格式
#             AccountAddress.from_hex(addr)
            
#         except Exception as e:
#             return (
#                 "无效的Aptos地址\n"
#                 "地址格式：0x + 64位十六进制字符\n"
#                 f"错误信息：{str(e)}"
#             )
            
#         # 检查红包是否超时
#         if time.time() - red_packet.created_time > self.plugin_config["max_time"]:
#             del self.red_packets[captcha]
#             return (
#                 "红包已过期\n"
#                 f"红包有效期为{self.plugin_config['max_time']}秒"
#             )
            
#         return None

#     def send_message(self, recv, message, log_level="info"):
#         """发送消息 - 同步版本"""
#         try:
#             getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
#             self.bot.send_text_msg(recv["from"], message)
#         except Exception as e:
#             logger.error(f"发送消息失败: {e}")

#     def send_error(self, recv, message):
#         """发送错误消息 - 同步版本"""
#         error_msg = (
#             f"\n❌ 操作失败\n"
#             f"━━━━━━━━━━━━━━━\n"
#             f"📛 错误信息：\n{message}\n"
#             f"━━━━━━━━━━━━━━━\n"
#             f"💡 发送 /redpack help 查看完整帮助"
#         )
#         self.send_message(recv, error_msg, "error")

#     def send_help(self, recv):
#         """发送帮助信息 - 同步版本"""
#         help_message = (
#             f"\n🎁 Aptos链上红包/空投系统\n"
#             f"━━━━━━━━━━━━━━━\n"
#             f"📢 功能介绍：\n"
#             f"在群内发送APT代币红包，支持随机金额分配\n"
#             f"可保存钱包地址，方便多次领取\n\n"
#             f"📝 发红包命令：\n"
#             f"• /redpack <APT数量> <红包个数>\n"
#             f"• /发红包 <APT数量> <红包个数>\n"
#             f"• /airdrop <APT数量> <红包个数>\n\n"
#             f"🎯 抢红包命令：\n"
#             f"• /claim <验证码> [钱包地址]\n"
#             f"• /抢红包 <验证码> [钱包地址]\n"
#             f"• /领取 <验证码> [钱包地址]\n\n"
#             f"📋 参数说明:\n"
#             f"• APT数量: {self.plugin_config['min_amount']} - {self.plugin_config['max_amount']} APT\n"
#             f"• 红包个数: 1 - {self.plugin_config['max_packet']} 个\n"
#             f"• 最小单个金额: {self.plugin_config['min_per_packet']} APT\n"
#             f"• 红包有效期: {self.plugin_config['max_time']}秒\n"
#             f"• 钱包地址: 可选参数，不填则使用历史地址\n\n"
#             f"💡 使用示例:\n"
#             f"1️⃣ 发送红包：\n"
#             f"   /redpack 10 5  (发10 APT分5个红包)\n\n"
#             f"2️⃣ 领取红包：\n"
#             f"   /claim abc12  (使用保存的地址)\n"
#             f"   /claim abc12 0x123...  (使用新地址)\n"
#             f"━━━━━━━━━━━━━━━"
#         )
#         self.send_message(recv, help_message)

#     async def run(self, recv):
#         """处理接收到的消息"""
#         try:
#             content = [item for item in recv["content"] if item.strip()]
#             logger.info(f"收到命令: {content}")
            
#             if not content:
#                 self.send_help(recv)
#                 return

#             command = content[0].lower()
            
#             # 检查是否是帮助命令
#             if len(content) > 1 and content[1] in ["帮助", "help", "查看帮助"]:
#                 self.send_help(recv)
#                 return
            
#             if command in ["/redpack", "/发红包", "/airdrop"]:
#                 try:
#                     await self._handle_send_packet(recv)
#                 except ValueError as e:
#                     self.send_error(recv, str(e))
#             elif command in ["/claim", "/抢红包", "/领取"]:
#                 try:
#                     await self._handle_claim_packet(recv)
#                 except ValueError as e:
#                     self.send_error(recv, str(e))
#             else:
#                 self.send_help(recv)

#         except Exception as e:
#             logger.error(f"处理命令时发生错误: {e}")
#             self.send_error(recv, f"处理命令失败: {e}")

#     async def _handle_claim_packet(self, recv):
#         """处理领取红包命令"""
#         try:
#             # 解析命令
#             captcha, address = self.parse_claim_command(recv["content"])

#             # 检查验证码有效性
#             if not captcha:
#                 self.send_error(recv, "验证码不能为空")
#                 return
            
#             if not self.is_valid_captcha(captcha):
#                 self.send_error(recv, "验证码格式错误\n请输入5位验证码")
#                 return

#             # 检查红包是否存在
#             if captcha not in self.red_packets:
#                 self.send_error(recv, "验证码错误或红包不存在\n请检查验证码是否正确")
#                 return
            
#             # 获取用户数据
#             user_data = self.user_db.get_user_data(recv["sender"])
            
#             # 处理地址逻辑
#             if not address and (not user_data or not user_data.get('WALLET_ADDRESS')):
#                 self.send_error(recv, "请提供钱包地址或先绑定地址")
#                 return
            
#             if not address:
#                 address = user_data['WALLET_ADDRESS']
#                 self.send_message(recv, f"\n📝 使用已保存的地址: {self.format_address(address)}")

#             # 验证红包
#             red_packet = self.red_packets[captcha]
#             error = self._validate_claim(recv, red_packet, address)
#             if error:
#                 self.send_error(recv, error)
#                 return
                
#             # 处理领取逻辑
#             try:
#                 apt_amount = red_packet.amount_list.pop()
#             except IndexError:
#                 self.send_error(recv, "红包已被抢完\n请等待下一个红包")
#                 return
            
#             # 更新用户地址
#             self.user_db.add_or_update_user({
#                 'wxid': recv["sender"],
#                 'wallet_address': address,
#                 'nickname': self.bot.get_contact_profile(recv["sender"])["nickname"]
#             })

#             try:
#                 # 转换地址格式
#                 receipt_address = AccountAddress.from_hex(address)
                
#                 # 执行转账
#                 txn_hash = await self.rest_client.bcs_transfer(
#                     self.contract_account,
#                     receipt_address,
#                     int(apt_amount * 100_000_000)
#                 )
#                 await self.rest_client.wait_for_transaction(txn_hash)
                
#                 # 记录领取
#                 red_packet.claimed.append((recv["sender"], address))
                
#                 # 发送成功消息
#                 self._send_claim_success(recv, address, apt_amount, txn_hash, red_packet)
                
#                 # 如果红包被抢完，清理资源
#                 if not red_packet.amount_list:
#                     self._cleanup_redpacket(captcha)
                
#             except Exception as e:
#                 logger.error(f"转账失败: {e}")
#                 # 恢复未领取的金额
#                 red_packet.amount_list.append(apt_amount)
#                 self.send_error(recv, f"转账失败: {str(e)}\n请检查地址是否正确")
                
#         except Exception as e:
#             logger.error(f"领取红包失败: {e}")
#             self.send_error(recv, str(e))

#     async def _handle_send_packet(self, recv):
#         """处理发送红包命令"""
#         try:
#             # 解析命令
#             total_amount, packet_count = self.parse_send_command(recv["content"])
            
#             # 检查发送者账户余额
#             try:
#                 balance = await self.rest_client.account_balance(self.contract_account.address())
#                 if balance < total_amount * 100_000_000:
#                     self.send_error(recv, (
#                         "合约账户余额不足\n"
#                         f"需要: {total_amount:.4f} APT\n"
#                         f"当前: {balance/100_000_000:.4f} APT"
#                     ))
#                     return
#             except Exception as e:
#                 logger.error(f"检查余额失败: {e}")
#                 self.send_error(recv, "检查余额失败，请稍后重试")
#                 return
                
#             # 生成红包信息
#             captcha, image_path = self._generate_captcha()
#             amount_list = self._split_amount(total_amount, packet_count)
            
#             red_packet = RedPacketInfo(
#                 total_amount=total_amount,
#                 amount=packet_count,
#                 sender=recv["sender"],
#                 amount_list=amount_list,
#                 claimed=[],
#                 created_time=time.time(),
#                 chatroom=recv["from"],
#                 sender_nick=self.bot.get_contact_profile(recv["sender"])["nickname"]
#             )
            
#             self.red_packets[captcha] = red_packet
            
#             # 发送红包消息
#             self._send_redpacket_message(recv, red_packet, captcha, image_path)
            
#         except Exception as e:
#             logger.error(f"发送红包失败: {e}")
#             self.send_error(recv, str(e))

#     def _send_redpacket_message(self, recv: dict, red_packet: RedPacketInfo, captcha: str, image_path: str):
#         """发送红包消息 - 同步版本"""
#         try:
#             # 发送验证码图片
#             self.bot.send_image_msg(recv["from"], image_path)
            
#             # 构建红包消息
#             message = (
#                 f"\n🧧 收到一个APT红包\n"
#                 f"━━━━━━━━━━━━━━━\n"
#                 f"👤 发送者: {red_packet.sender_nick}\n"
#                 f"💰 金额: {red_packet.total_amount:.4f} APT\n"
#                 f"📦 数量: {red_packet.amount}个\n"
#                 f"🎯 口令: {captcha}\n"
#                 f"━━━━━━━━━━━━━━━\n"
#                 f"📝 使用以下命令领取:\n"
#                 f"/claim {captcha} <钱包地址>\n"
#                 f"或\n"
#                 f"/抢红包 {captcha} <钱包地址>\n"
#                 f"提示: 不填地址则使用上次地址"
#             )
#             self.send_message(recv, message)
            
#         except Exception as e:
#             logger.error(f"发送红包消息失败: {e}")
#             raise

#     @staticmethod
#     def _ensure_cache_directory() -> None:
#         """确保缓存目录存在"""
#         cache_path = Path("resources/cache")
#         if not cache_path.exists():
#             logger.info("创建cache文件夹")
#             cache_path.mkdir(parents=True, exist_ok=True)

#     @staticmethod
#     def format_address(address: str, length: int = 6) -> str:
#         """格式化地址显示"""
#         if len(address) <= length * 2:
#             return address
#         return f"{address[:length]}...{address[-length:]}"

#     @staticmethod
#     def _generate_captcha() -> Tuple[str, str]:
#         """生成验证码和图片"""
#         chars = "abdfghkmnpqtwxy2346789"
#         captcha = ''.join(random.sample(chars, 5))
        
#         image = ImageCaptcha().generate_image(captcha)
#         path = f"resources/cache/{captcha}.jpg"
#         image.save(path)
        
#         return captcha, os.path.abspath(path)

#     def _split_amount(self, total: float, count: int) -> List[float]:
#         """随机分配红包金额"""
#         # 转换为最小单位(0.000001 APT)进行计算
#         min_unit = self.plugin_config["min_per_packet"]
#         total_units = int(total / min_unit)
#         count_units = int(count)
        
#         if total_units < count_units:
#             raise ValueError("红包总金额不能小于红包个数")
            
#         # 确保每个红包至少有一个最小单位
#         amounts = [1] * count_units
#         remaining_units = total_units - count_units
        
#         # 随机分配剩余金额
#         while remaining_units > 0:
#             for i in range(count_units):
#                 if remaining_units <= 0:
#                     break
#                 rand_amount = random.randint(0, remaining_units)
#                 amounts[i] += rand_amount
#                 remaining_units -= rand_amount
        
#         # 转换回APT
#         return [amount * min_unit for amount in amounts]

#     async def _create_expiry_task(self, captcha: str, chat_room: str):
#         """创建单个红包的过期检查任务"""
#         try:
#             task = asyncio.create_task(self._check_expiry(captcha, chat_room))
#             self.expiry_tasks.add(task)
#             task.add_done_callback(self.expiry_tasks.discard)
#             return task
#         except Exception as e:
#             logger.error(f"创建过期检查任务失败: {e}")
#             return None

#     def __del__(self):

#         """清理资源"""
#         try:
#             # 确保关闭数据库连接
#             if hasattr(self, 'user_db'):
#                 self.user_db.__del__()
#             logger.info("Aptos红包插件资源已清理")
#         except Exception as e:
#             logger.error(f"清理资源时发生错误: {e}")






class aptos_airdrop(PluginInterface):
    def __init__(self):
        try:
            # ... 其他初始化代码保持不变 ...

            # 初始化事件循环
            self.loop = None
            self.running = False

        except Exception as e:
            logger.error(f"初始化插件失败: {e}")
            raise

    async def start(self):
        """启动插件"""
        try:
            self.running = True
            self.loop = asyncio.get_running_loop()
            logger.info("Aptos红包插件启动成功")
        except Exception as e:
            logger.error(f"启动插件失败: {e}")
            raise

    async def stop(self):
        """停止插件"""
        self.running = False
        logger.info("Aptos红包插件停止")

    def send_message(self, recv, message, log_level="info"):
        """同步发送消息"""
        try:
            getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
            self.bot.send_text_msg(recv["from"], message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")

    async def run(self, recv):
        """处理接收到的消息"""
        if not self.running:
            logger.error("插件未启动")
            return

        try:
            content = [item for item in recv["content"] if item.strip()]
            logger.info(f"收到命令: {content}")
            
            if not content:
                self.send_help(recv)
                return

            command = content[0].lower()
            
            # 检查是否是帮助命令
            if len(content) > 1 and content[1] in ["帮助", "help", "查看帮助"]:
                self.send_help(recv)
                return
            
            if command in ["/redpack", "/发红包", "/airdrop"]:
                try:
                    # 将异步操作包装在同步操作中
                    total_amount, packet_count = self.parse_send_command(content)
                    await self._handle_send_packet(recv, total_amount, packet_count)
                except ValueError as e:
                    self.send_error(recv, str(e))
                except Exception as e:
                    logger.error(f"处理发红包命令失败: {e}")
                    self.send_error(recv, "处理命令失败，请重试")
            elif command in ["/claim", "/抢红包", "/领取"]:
                try:
                    # 将异步操作包装在同步操作中
                    captcha, address = self.parse_claim_command(content)
                    if self.loop and self.loop.is_running():
                        await self._handle_claim_packet(recv, captcha, address)
                    else:
                        self.send_error(recv, "系统繁忙，请稍后重试")
                except ValueError as e:
                    self.send_error(recv, str(e))
                except Exception as e:
                    logger.error(f"处理领取红包命令失败: {e}")
                    self.send_error(recv, "处理命令失败，请重试")
            else:
                self.send_help(recv)

        except Exception as e:
            logger.error(f"处理命令时发生错误: {e}")
            self.send_error(recv, "处理命令失败，请稍后重试")

    async def _handle_send_packet(self, recv, total_amount: float, packet_count: int):
        """处理发送红包命令"""
        if not self.loop or not self.loop.is_running():
            self.send_error(recv, "系统繁忙，请稍后重试")
            return

        try:
            # 检查发送者账户余额
            balance = await self.rest_client.account_balance(self.contract_account.address())
            if balance < total_amount * 100_000_000:
                self.send_error(recv, (
                    "合约账户余额不足\n"
                    f"需要: {total_amount:.4f} APT\n"
                    f"当前: {balance/100_000_000:.4f} APT"
                ))
                return

            # 生成红包信息
            captcha, image_path = self._generate_captcha()
            amount_list = self._split_amount(total_amount, packet_count)
            
            red_packet = RedPacketInfo(
                total_amount=total_amount,
                amount=packet_count,
                sender=recv["sender"],
                amount_list=amount_list,
                claimed=[],
                created_time=time.time(),
                chatroom=recv["from"],
                sender_nick=self.bot.get_contact_profile(recv["sender"])["nickname"]
            )
            
            self.red_packets[captcha] = red_packet
            
            # 同步发送消息
            self._send_redpacket_message(recv, red_packet, captcha, image_path)
            
        except Exception as e:
            logger.error(f"发送红包失败: {e}")
            self.send_error(recv, "发送红包失败，请重试")

    def _send_redpacket_message(self, recv: dict, red_packet: RedPacketInfo, captcha: str, image_path: str):
        """发送红包消息 - 同步版本"""
        try:
            # 发送验证码图片
            self.bot.send_image_msg(recv["from"], image_path)
            
            # 构建红包消息
            message = (
                f"\n🧧 收到一个APT红包\n"
                f"━━━━━━━━━━━━━━━\n"
                f"👤 发送者: {red_packet.sender_nick}\n"
                f"💰 金额: {red_packet.total_amount:.4f} APT\n"
                f"📦 数量: {red_packet.amount}个\n"
                f"🎯 口令: {captcha}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📝 使用以下命令领取:\n"
                f"/claim {captcha} <钱包地址>\n"
                f"或\n"
                f"/抢红包 {captcha} <钱包地址>\n"
                f"提示: 不填地址则使用上次地址"
            )
            self.send_message(recv, message)
            
        except Exception as e:
            logger.error(f"发送红包消息失败: {e}")
            raise

    async def _handle_claim_packet(self, recv, captcha: str, address: Optional[str]):
        """处理领取红包命令"""
        if not self.loop or not self.loop.is_running():
            self.send_error(recv, "系统繁忙，请稍后重试")
            return

        try:
            # 获取用户数据
            user_data = self.user_db.get_user_data(recv["sender"])
            
            # 处理地址逻辑
            if not address and (not user_data or not user_data.get('WALLET_ADDRESS')):
                self.send_error(recv, "请提供钱包地址或先绑定地址")
                return
            
            if not address:
                address = user_data['WALLET_ADDRESS']
                self.send_message(recv, f"\n📝 使用已保存的地址: {self.format_address(address)}")

            # 验证红包
            if captcha not in self.red_packets:
                self.send_error(recv, "验证码错误或红包不存在")
                return

            red_packet = self.red_packets[captcha]
            error = self._validate_claim(recv, red_packet, address)
            if error:
                self.send_error(recv, error)
                return

            # 处理领取逻辑
            try:
                apt_amount = red_packet.amount_list.pop()
            except IndexError:
                self.send_error(recv, "红包已被抢完")
                return

            try:
                # 执行转账
                receipt_address = AccountAddress.from_hex(address)
                txn_hash = await self.rest_client.bcs_transfer(
                    self.contract_account,
                    receipt_address,
                    int(apt_amount * 100_000_000)
                )
                await self.rest_client.wait_for_transaction(txn_hash)

                # 更新数据
                self.user_db.add_or_update_user({
                    'wxid': recv["sender"],
                    'wallet_address': address,
                    'nickname': self.bot.get_contact_profile(recv["sender"])["nickname"]
                })
                
                red_packet.claimed.append((recv["sender"], address))

                # 发送成功消息
                self._send_claim_success(recv, address, apt_amount, txn_hash, red_packet)

                # 检查是否抢完
                if not red_packet.amount_list:
                    self._cleanup_redpacket(captcha)

            except Exception as e:
                logger.error(f"转账失败: {e}")
                red_packet.amount_list.append(apt_amount)  # 恢复金额
                self.send_error(recv, f"转账失败，请重试")

        except Exception as e:
            logger.error(f"领取红包失败: {e}")
            self.send_error(recv, "领取失败，请重试")

    def _send_claim_success(self, recv, address, amount, txn_hash, red_packet):
        """发送领取成功消息 - 同步版本"""
        try:
            # 发送成功消息
            success_msg = (
                f"\n🎉 恭喜抢到了 {amount:.4f} APT！\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💰 转入地址: {self.format_address(address)}\n"
                f"📜 交易Hash: {self.format_address(txn_hash)}\n"
                f"🔍 浏览器: {self.networks[self.current_network]['explorer_url']}/txn/{txn_hash}"
            )
            self.send_message(recv, success_msg)

        except Exception as e:
            logger.error(f"发送成功消息失败: {e}")
