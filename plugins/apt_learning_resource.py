import yaml
from loguru import logger
import pywxdll
from utils.plugin_interface import PluginInterface
from typing import Tuple, Optional

class apt_learning_resource(PluginInterface):
    def __init__(self):
        # 加载插件配置
        config_path = "plugins/apt_learning.yml"
        with open(config_path, "r", encoding="utf-8") as f:
            self.plugin_config = yaml.safe_load(f.read())
        
        # 初始化资源和帮助信息
        self.resources = self.plugin_config["resources"]
        self.command_help = self.plugin_config["command_help"]

        # 加载主配置
        self.config = self.load_config()
        self.bot = pywxdll.Pywxdll(self.config["ip"], self.config["port"])
    
    def parse_command(self, content: list) -> Optional[str]:
        """
        解析命令参数
        返回: 资源类型 (notion/google_drive/None)
        """
        try:
            # 移除命令名
            args = [arg.lower() for arg in content[1:] if arg.strip()]
            
            if not args:
                return None  # 返回所有资源
                
            resource_type = args[0]
            if resource_type in ["notion", "文档"]:
                return "notion"
            elif resource_type in ["drive", "google", "谷歌"]:
                return "google_drive"
            else:
                raise ValueError("未知的资源类型")
                
        except ValueError as e:
            raise ValueError(f"命令解析错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"命令解析错误: {str(e)}")

    async def run(self, recv):
        try:
            content = [item for item in recv["content"] if item.strip()]
            logger.info(f"收到命令: {content}")

            # 解析命令
            resource_type = self.parse_command(content)
            
            # 发送资源
            await self.send_resources(recv, resource_type)

        except Exception as e:
            logger.error(f"处理命令时发生错误: {e}")
            await self.send_error(recv, f"处理命令失败: {e}")
            await self.send_help(recv)

    async def send_resources(self, recv, resource_type: Optional[str] = None):
        """发送学习资源消息"""
        if resource_type == "notion":
            resources_msg = (
                f"\n📚 Aptos Notion 文档\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔍 Move语言学习文档：\n"
                f"{self.resources['notion']}\n"
                f"━━━━━━━━━━━━━━━"
            )
        elif resource_type == "google_drive":
            resources_msg = (
                f"\n📚 Aptos Google Drive 资源\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📁 资源下载地址：\n"
                f"{self.resources['google_drive']}\n"
                f"━━━━━━━━━━━━━━━"
            )
        else:
            # 默认发送所有资源
            resources_msg = (
                f"\n📚 Aptos 学习资源\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔍 Notion 文档：\n"
                f"{self.resources['notion']}\n\n"
                f"📁 Google Drive 资源：\n"
                f"{self.resources['google_drive']}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💡 这些资源将帮助您更好地了解 Aptos 生态系统"
            )
        await self.send_message(recv, resources_msg)

    async def send_help(self, recv):
        """发送帮助信息"""
        help_message = (
            f"\n📚 Aptos 学习资源帮助\n"
            f"━━━━━━━━━━━━━━━\n"
            f"命令格式：\n"
            f"1️⃣ 查看所有资源：\n"
            f"   /aptlearn\n\n"
            f"2️⃣ 只看 Notion 文档：\n"
            f"   /aptlearn notion\n"
            f"   /aptlearn 文档\n\n"
            f"3️⃣ 只看 Google Drive：\n"
            f"   /aptlearn drive\n"
            f"   /aptlearn 谷歌\n"
            f"━━━━━━━━━━━━━━━"
        )
        await self.send_message(recv, help_message)

    async def send_message(self, recv, message, log_level="info"):
        """发送消息的通用方法"""
        getattr(logger, log_level)(f'[发送信息]{message}| [发送到] {recv["from"]}')
        self.bot.send_text_msg(recv["from"], message)

    async def send_error(self, recv, message):
        """发送错误消息"""
        error_msg = (
            f"\n❌ 操作失败\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📛 错误信息：{message}\n"
            f"━━━━━━━━━━━━━━━"
        )
        await self.send_message(recv, error_msg, "error")