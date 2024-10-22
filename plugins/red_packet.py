# import os
# import random
# import time

# import yaml
# from captcha.image import ImageCaptcha
# from loguru import logger

# import pywxdll
# from utils.database import BotDatabase
# from utils.plugin_interface import PluginInterface


# class red_packet(PluginInterface):
#     def __init__(self):
#         config_path = "plugins/red_packet.yml"
#         with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
#             config = yaml.safe_load(f.read())

#         self.max_point = config["max_point"]  # 最大积分
#         self.min_point = config["min_point"]  # 最小积分
#         self.max_packet = config["max_packet"]  # 最大红包数量
#         self.max_time = config["max_time"]  # 红包超时时间

#         main_config_path = "main_config.yml"
#         with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
#             main_config = yaml.safe_load(f.read())

#         self.ip = main_config["ip"]  # 机器人ip
#         self.port = main_config["port"]  # 机器人端口
#         self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

#         self.command_prefix = main_config["command_prefix"]

#         self.db = BotDatabase()  # 实例化机器人数据库类

#         cache_path = "resources/cache"  # 检测是否有cache文件夹
#         if not os.path.exists(cache_path):
#             logger.info("检测到未创建cache缓存文件夹")
#             os.makedirs(cache_path)
#             logger.info("已创建cache文件夹")

#         self.red_packets = {}  # 红包列表

#     async def run(self, recv):
#         if len(recv["content"]) == 3:  # 判断是否为红包指令
#             self.send_red_packet(recv)
#         elif len(recv["content"]) == 2:  # 判断是否为抢红包指令
#             self.grab_red_packet(recv)
#         else:  # 指令格式错误
#             self.send_friend_or_group(
#                 recv, "\n❌命令格式错误！请查看菜单获取正确命令格式"
#             )

#     def send_red_packet(self, recv):
#         red_packet_sender = recv["sender"]

#         # 判断是否有错误
#         error = ""
#         if recv["fromType"] == 'friend':
#             error = "\n❌红包只能在群里发！"
#         elif not recv["content"][1].isdigit() or not recv["content"][2].isdigit():
#             error = "\n❌指令格式错误！\n 积分红包！🧧\n⚙️发红包指令：发红包 积分数 红包数\n⚙️抢红包指令：抢红包 验证码！"
#         elif int(recv["content"][1]) > self.max_point or int(recv["content"][1]) < self.min_point:
#             error = f"\n⚠️积分无效！最大{self.max_point}，最小{self.min_point}！"
#         elif int(recv["content"][2]) > self.max_packet:
#             error = f"\n⚠️红包数量无效！最大{self.max_packet}！"
#         elif int(recv["content"][2]) > int(recv["content"][1]):
#             error = "\n❌红包数量不能大于红包积分！"

#         # 判断是否有足够积分
#         if not error:
#             if self.db.get_points(red_packet_sender) < int(recv["content"][1]):
#                 error = "\n❌积分不足！"

#         if not error:
#             red_packet_points = int(recv["content"][1])  # 红包积分
#             red_packet_amount = int(recv["content"][2])  # 红包数量
#             red_packet_chatroom = recv["from"]  # 红包所在群聊

#             red_packet_sender_nick = self.bot.get_contact_profile(red_packet_sender)["nickname"]  # 获取昵称

#             red_packet_points_list = self.split_integer(
#                 red_packet_points, red_packet_amount
#             )  # 随机分红包积分

#             chr_5, captcha_path = self.generate_captcha()  # 生成口令
#             captcha_path = os.path.abspath(captcha_path)  # 获取口令路径

#             new_red_packet = {
#                 "points": red_packet_points,
#                 "amount": red_packet_amount,
#                 "sender": red_packet_sender,
#                 "list": red_packet_points_list,
#                 "grabbed": [],
#                 "time": time.time(),
#                 "chatroom": red_packet_chatroom,
#                 "sender_nick": red_packet_sender_nick,
#             }  # 红包信息

#             self.red_packets[chr_5] = new_red_packet  # 把红包放入红包列表
#             self.db.add_points(red_packet_sender, red_packet_points * -1)  # 扣除积分

#             # 组建信息
#             out_message = f"\n{red_packet_sender_nick} 发送了一个红包！\n\n🧧红包金额：{red_packet_points}点积分\n🧧红包数量：{red_packet_amount}个\n\n🧧红包口令请见下图！\n\n快输入指令来抢红包！\n指令：{self.command_prefix}抢红包 口令"

#             # 发送信息
#             self.bot.send_text_msg(recv["from"], out_message)
#             logger.info(
#                 f'[发送信息] (红包口令图片) {captcha_path} | [发送到] {recv["from"]}'
#             )

#             self.bot.send_image_msg(recv["from"], captcha_path)


#         else:
#             self.send_friend_or_group(recv, error)  # 发送错误信息

#     def grab_red_packet(self, recv):
#         red_packet_grabber = recv["sender"]

#         req_captcha = recv["content"][1]

#         # 判断是否有错误
#         error = ""
#         if req_captcha not in self.red_packets.keys():
#             error = "\n❌口令错误或无效！"
#         elif not self.red_packets[req_captcha]["list"]:
#             error = "\n⚠️红包已被抢完！"
#         elif recv['fromType'] == 'friend':
#             error = "\n❌红包只能在群里抢！"
#         elif red_packet_grabber in self.red_packets[req_captcha]["grabbed"]:
#             error = "\n⚠️你已经抢过这个红包了！"
#         elif self.red_packets[req_captcha]["sender"] == red_packet_grabber:
#             error = "\n❌不能抢自己的红包！"

#         if not error:
#             try:  # 抢红包
#                 grabbed_points = self.red_packets[req_captcha][
#                     "list"
#                 ].pop()  # 抢到的积分
#                 self.red_packets[req_captcha]["grabbed"].append(
#                     red_packet_grabber
#                 )  # 把抢红包的人加入已抢列表
#                 red_packet_grabber_nick = self.bot.get_contact_profile(red_packet_grabber)["nickname"]  # 获取昵称

#                 self.db.add_points(red_packet_grabber, grabbed_points)  # 增加积分

#                 # 组建信息
#                 out_message = f"\n🧧恭喜 {red_packet_grabber_nick} 抢到了 {grabbed_points} 点积分！"
#                 self.send_friend_or_group(recv, out_message)

#                 # 判断是否抢完
#                 if not self.red_packets[req_captcha]["list"]:
#                     self.red_packets.pop(req_captcha)

#             except IndexError:
#                 error = "\n❌红包已被抢完！"
#                 self.send_friend_or_group(recv, error)

#                 return

#         else:
#             # 发送错误信息
#             self.send_friend_or_group(recv, error)

#             return

#     @staticmethod
#     def generate_captcha():  # 生成口令
#         chr_all = [
#             "a",
#             "b",
#             "d",
#             "f",
#             "g",
#             "h",
#             "k",
#             "m",
#             "n",
#             "p",
#             "q",
#             "t",
#             "w",
#             "x",
#             "y",
#             "2",
#             "3",
#             "4",
#             "6",
#             "7",
#             "8",
#             "9",
#         ]
#         chr_5 = "".join(random.sample(chr_all, 5))
#         captcha_image = ImageCaptcha().generate_image(chr_5)
#         path = f"resources/cache/{chr_5}.jpg"
#         captcha_image.save(path)

#         return chr_5, path

#     @staticmethod
#     def split_integer(num, count):
#         # 初始化每个数为1
#         result = [1] * count
#         remaining = num - count

#         # 随机分配剩余的部分
#         while remaining > 0:
#             index = random.randint(0, count - 1)
#             result[index] += 1
#             remaining -= 1

#         return result

#     def expired_red_packets_check(self):  # 检查是否有超时红包
#         logger.info("[计划任务]检查是否有超时的红包")
#         for key in list(self.red_packets.keys()):
#             if (time.time() - self.red_packets[key]["time"] > self.max_time):  # 判断是否超时

#                 red_packet_sender = self.red_packets[key]["sender"]  # 获取红包发送人
#                 red_packet_points_left_sum = sum(self.red_packets[key]["list"])  # 获取剩余积分
#                 red_packet_chatroom = self.red_packets[key]["chatroom"]  # 获取红包所在群聊
#                 red_packet_sender_nick = self.red_packets[key]["sender_nick"]  # 获取红包发送人昵称

#                 self.db.add_points(red_packet_sender, red_packet_points_left_sum)  # 归还积分
#                 self.red_packets.pop(key)  # 删除红包
#                 logger.info("[红包]有红包超时，已归还积分！")  # 记录日志

#                 # 组建信息并发送
#                 out_message = f"\n🧧发现有红包 {key} 超时！已归还剩余 {red_packet_points_left_sum} 积分给 {red_packet_sender_nick}"
#                 self.bot.send_text_msg(red_packet_chatroom, out_message)
#                 logger.info(f"[发送信息]{out_message}| [发送到] {red_packet_chatroom}")

#     def send_friend_or_group(self, recv, out_message="null"):
#         if recv["fromType"] == "chatroom":  # 判断是群还是私聊
#             logger.info(f'[发送@信息]{out_message}| [发送到] {recv["from"]}')
#             self.bot.send_at_msg(recv["from"], "\n" + out_message, [recv["sender"]])

#         else:
#             logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
#             self.bot.send_text_msg(recv["from"], out_message)  # 发送
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import os
import random
import time
from pathlib import Path

import yaml
from captcha.image import ImageCaptcha
from loguru import logger
import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface

@dataclass
class RedPacketConfig:
    """红包配置数据类"""
    max_point: int
    min_point: int
    max_packet: int
    max_time: int
    command_prefix: str
    ip: str
    port: int

@dataclass
class RedPacketInfo:
    """红包信息数据类"""
    points: int
    amount: int
    sender: str
    points_list: List[int]
    grabbed: List[str]
    created_time: float
    chatroom: str
    sender_nick: str

class RedPacketPlugin(PluginInterface):
    """红包插件实现类"""
    
    def __init__(self):
        """初始化红包插件"""
        self.config = self._load_config()
        self.bot = pywxdll.Pywxdll(self.config.ip, self.config.port)
        self.db = BotDatabase()
        self.red_packets: Dict[str, RedPacketInfo] = {}
        self._ensure_cache_directory()

    def _load_config(self) -> RedPacketConfig:
        """加载配置文件"""
        try:
            with open("plugins/red_packet.yml", "r", encoding="utf-8") as f:
                plugin_config = yaml.safe_load(f)
            
            with open("main_config.yml", "r", encoding="utf-8") as f:
                main_config = yaml.safe_load(f)
            
            return RedPacketConfig(
                max_point=plugin_config["max_point"],
                min_point=plugin_config["min_point"],
                max_packet=plugin_config["max_packet"],
                max_time=plugin_config["max_time"],
                command_prefix=main_config["command_prefix"],
                ip=main_config["ip"],
                port=main_config["port"]
            )
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    @staticmethod
    def _ensure_cache_directory() -> None:
        """确保缓存目录存在"""
        cache_path = Path("resources/cache")
        if not cache_path.exists():
            logger.info("创建cache缓存文件夹")
            cache_path.mkdir(parents=True, exist_ok=True)

    async def run(self, recv: dict) -> None:
        """处理红包命令"""
        content_length = len(recv["content"])
        
        try:
            if content_length == 3:
                await self._handle_send_packet(recv)
            elif content_length == 2:
                await self._handle_grab_packet(recv)
            else:
                await self._send_message(recv, "\n❌命令格式错误！请查看菜单获取正确命令格式")
        except Exception as e:
            logger.error(f"处理红包命令出错: {e}")
            await self._send_message(recv, f"\n❌处理命令出错: {str(e)}")

    async def _handle_send_packet(self, recv: dict) -> None:
        """处理发红包命令"""
        error = self._validate_send_packet(recv)
        if error:
            await self._send_message(recv, error)
            return

        try:
            points = int(recv["content"][1])
            amount = int(recv["content"][2])
            
            # 生成红包信息
            captcha, red_packet = await self._create_red_packet(recv, points, amount)
            self.red_packets[captcha] = red_packet
            
            # 扣除积分
            self.db.add_points(recv["sender"], -points)
            
            # 发送红包消息
            await self._send_red_packet_message(recv, red_packet, captcha)
            
        except Exception as e:
            logger.error(f"创建红包失败: {e}")
            await self._send_message(recv, f"\n❌创建红包失败: {str(e)}")

    def _validate_send_packet(self, recv: dict) -> Optional[str]:
        """验证发红包参数"""
        if recv["fromType"] == 'friend':
            return "\n❌红包只能在群里发！"
            
        try:
            points = int(recv["content"][1])
            amount = int(recv["content"][2])
        except ValueError:
            return "\n❌指令格式错误！\n积分红包！🧧\n⚙️发红包指令：发红包 积分数 红包数\n⚙️抢红包指令：抢红包 验证码！"

        if not (self.config.min_point <= points <= self.config.max_point):
            return f"\n⚠️积分无效！最大{self.config.max_point}，最小{self.config.min_point}！"
            
        if amount > self.config.max_packet:
            return f"\n⚠️红包数量无效！最大{self.config.max_packet}！"
            
        if amount > points:
            return "\n❌红包数量不能大于红包积分！"
            
        if self.db.get_points(recv["sender"]) < points:
            return "\n❌积分不足！"
            
        return None

    async def _handle_grab_packet(self, recv: dict) -> None:
        """处理抢红包命令"""
        captcha = recv["content"][1]
        error = self._validate_grab_packet(recv, captcha)
        
        if error:
            await self._send_message(recv, error)
            return

        try:
            red_packet = self.red_packets[captcha]
            points = red_packet.points_list.pop()
            red_packet.grabbed.append(recv["sender"])
            
            # 增加积分
            self.db.add_points(recv["sender"], points)
            
            # 发送抢红包成功消息
            grabber_nick = self.bot.get_contact_profile(recv["sender"])["nickname"]
            await self._send_message(recv, f"\n🧧恭喜 {grabber_nick} 抢到了 {points} 点积分！")
            
            # 检查红包是否抢完
            if not red_packet.points_list:
                del self.red_packets[captcha]
                
        except Exception as e:
            logger.error(f"抢红包失败: {e}")
            await self._send_message(recv, "\n❌抢红包失败，请重试！")

    def _validate_grab_packet(self, recv: dict, captcha: str) -> Optional[str]:
        """验证抢红包参数"""
        if captcha not in self.red_packets:
            return "\n❌口令错误或无效！"
            
        red_packet = self.red_packets[captcha]
        
        if not red_packet.points_list:
            return "\n⚠️红包已被抢完！"
            
        if recv['fromType'] == 'friend':
            return "\n❌红包只能在群里抢！"
            
        if recv["sender"] in red_packet.grabbed:
            return "\n⚠️你已经抢过这个红包了！"
            
        if recv["sender"] == red_packet.sender:
            return "\n❌不能抢自己的红包！"
            
        return None

    @staticmethod
    def _generate_captcha() -> Tuple[str, str]:
        """生成验证码"""
        chars = "abdfghkmnpqtwxy2346789"
        captcha = ''.join(random.sample(chars, 5))
        
        image = ImageCaptcha().generate_image(captcha)
        path = f"resources/cache/{captcha}.jpg"
        image.save(path)
        
        return captcha, os.path.abspath(path)

    @staticmethod
    def _split_points(total: int, count: int) -> List[int]:
        """随机分配积分"""
        if count <= 0 or total < count:
            raise ValueError("Invalid points or count")
            
        points = [1] * count
        remaining = total - count
        
        while remaining > 0:
            index = random.randint(0, count - 1)
            points[index] += 1
            remaining -= 1
            
        return points

    async def check_expired_packets(self) -> None:
        """检查过期红包"""
        logger.info("[计划任务]检查是否有超时的红包")
        current_time = time.time()
        
        expired_packets = [
            (key, packet) for key, packet in self.red_packets.items()
            if current_time - packet.created_time > self.config.max_time
        ]
        
        for key, packet in expired_packets:
            remaining_points = sum(packet.points_list)
            self.db.add_points(packet.sender, remaining_points)
            del self.red_packets[key]
            
            message = (
                f"\n🧧发现有红包 {key} 超时！"
                f"已归还剩余 {remaining_points} 积分给 {packet.sender_nick}"
            )
            self.bot.send_text_msg(packet.chatroom, message)
            logger.info(f"[红包]红包{key}超时，已归还{remaining_points}积分给{packet.sender_nick}")

    async def _send_message(self, recv: dict, message: str) -> None:
        """发送消息"""
        if recv["fromType"] == "chatroom":
            logger.info(f'[发送@信息]{message}| [发送到] {recv["from"]}')
            self.bot.send_at_msg(recv["from"], "\n" + message, [recv["sender"]])
        else:
            logger.info(f'[发送信息]{message}| [发送到] {recv["from"]}')
            self.bot.send_text_msg(recv["from"], message)