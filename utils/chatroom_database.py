#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from loguru import logger

from utils.singleton import singleton

@singleton
class ChatroomDatabase:
    def __init__(self, db_path="chatroomdata.db"):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            logger.warning("检测到聊天室数据库不存在，正在创建数据库")
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE CHATROOMDATA (
                    GROUP_WXID TEXT, 
                    USER_WXID TEXT,
                    USERNAME TEXT,
                    MESSAGE_CONTENT TEXT,
                    MESSAGE_TIMESTAMP TEXT,
                    MESSAGE_TYPE TEXT,
                    JOIN_TIME TEXT,
                    NICKNAME_CHANGE_COUNT INTEGER,
                    IS_WHITELIST INTEGER,
                    IS_BLACKLIST INTEGER,
                    IS_WARNED INTEGER,
                    BOT_CONFIDENCE REAL,
                    PRIMARY KEY (GROUP_WXID, USER_WXID)
                )
            """)
            conn.commit()
            c.close()
            conn.close()
            logger.warning("已创建聊天室数据库")

        self.database = sqlite3.connect(self.db_path, check_same_thread=False)

        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="chatroomdb")

    def _execute_in_queue(self, method, *args, **kwargs):
        future = self.executor.submit(method, *args, **kwargs)
        try:
            return future.result(timeout=20)
        except Exception as error:
            logger.error(f"数据库操作错误: {error}")
            return None

    # 添加信息
    def add_message(self, group_wxid, user_wxid, username, content, msg_type):
        return self._execute_in_queue(self._add_message, group_wxid, user_wxid, username, content, msg_type)

    def _add_message(self, group_wxid, user_wxid, username, content, msg_type):
        cursor = self.database.cursor()
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT OR REPLACE INTO CHATROOMDATA 
                (GROUP_WXID, USER_WXID, USERNAME, MESSAGE_CONTENT, MESSAGE_TIMESTAMP, MESSAGE_TYPE,
                 JOIN_TIME, NICKNAME_CHANGE_COUNT, IS_WHITELIST, IS_BLACKLIST, IS_WARNED, BOT_CONFIDENCE)
                VALUES (?, ?, ?, ?, ?, ?, 
                        COALESCE((SELECT JOIN_TIME FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), ?),
                        COALESCE((SELECT NICKNAME_CHANGE_COUNT FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                        COALESCE((SELECT IS_WHITELIST FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                        COALESCE((SELECT IS_BLACKLIST FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                        COALESCE((SELECT IS_WARNED FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                        COALESCE((SELECT BOT_CONFIDENCE FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0.0))
            """, (group_wxid, user_wxid, username, content, current_time, msg_type,
                  group_wxid, user_wxid, current_time,
                  group_wxid, user_wxid,
                  group_wxid, user_wxid,
                  group_wxid, user_wxid,
                  group_wxid, user_wxid,
                  group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"消息已添加: {group_wxid}, {user_wxid}")
            return True
        except sqlite3.Error as e:
            logger.error(f"添加消息时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    # 获取用户数据
    def get_user_data(self, group_wxid, user_wxid):
        return self._execute_in_queue(self._get_user_data, group_wxid, user_wxid)

    def _get_user_data(self, group_wxid, user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("""
                SELECT * FROM CHATROOMDATA 
                WHERE GROUP_WXID=? AND USER_WXID=?
            """, (group_wxid, user_wxid))
            data = cursor.fetchone()
            if data:
                logger.debug(f"原始用户数据: {data}")
                logger.debug(f"查询到的字段: {len(data)}")
            return data
        except sqlite3.Error as e:
            logger.error(f"获取用户数据时发生SQL错误: {e}")
            return None
        finally:
            cursor.close()

# 设置白名单列表
    def set_whitelist(self, group_wxid, user_wxid, status):
        return self._execute_in_queue(self._set_whitelist, group_wxid, user_wxid, status)

    def _set_whitelist(self, group_wxid, user_wxid, status):
        cursor = self.database.cursor()
        try:
            cursor.execute("""
                UPDATE CHATROOMDATA 
                SET IS_WHITELIST=? 
                WHERE GROUP_WXID=? AND USER_WXID=?
            """, (status, group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"[数据库] {group_wxid}, {user_wxid} 白名单状态已设置为 {status}")
            return True
        except sqlite3.Error as e:
            logger.error(f"设置白名单状态时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    # 获取白名单列表
    def get_whitelist(self, group_wxid, user_wxid):
        return self._execute_in_queue(self._get_whitelist, group_wxid, user_wxid)

    def _get_whitelist(self, group_wxid, user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("""
                SELECT IS_WHITELIST 
                FROM CHATROOMDATA 
                WHERE GROUP_WXID=? AND USER_WXID=?
            """, (group_wxid, user_wxid))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"获取白名单状态时发生SQL错误: {e}")
            return None
        finally:
            cursor.close()

    # 获取用户列表
    def get_user_list(self, group_wxid):
        return self._execute_in_queue(self._get_user_list, group_wxid)

    def _get_user_list(self, group_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT * FROM CHATROOMDATA WHERE GROUP_WXID=?", (group_wxid,))
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            logger.error(f"获取用户列表时发生SQL错误: {e}")
            return []
        finally:
            cursor.close()

    # 获取用户数量
    def get_user_count(self, group_wxid):
        return self._execute_in_queue(self._get_user_count, group_wxid)

    def _get_user_count(self, group_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM CHATROOMDATA WHERE GROUP_WXID=?", (group_wxid,))
            result = cursor.fetchone()[0]
            return result
        except sqlite3.Error as e:
            logger.error(f"获取用户数量时发生SQL错误: {e}")
            return 0
        finally:
            cursor.close()

    def _add_column(self, column_name: str, column_type: str):
        cursor = self.database.cursor()
        try:
            cursor.execute(f"ALTER TABLE CHATROOMDATA ADD COLUMN {column_name} {column_type}")
            self.database.commit()
            logger.info(f"[数据库] 已添加列 {column_name}")
        except sqlite3.Error as e:
            logger.error(f"添加列时发生SQL错误: {e}")
        finally:
            cursor.close()

    # 添加列
    def add_column(self, column_name: str, column_type: str):
        return self._execute_in_queue(self._add_column, column_name, column_type)

    def _get_columns(self):
        cursor = self.database.cursor()
        try:
            cursor.execute("PRAGMA table_info(CHATROOMDATA)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            return column_names
        except sqlite3.Error as e:
            logger.error(f"获取列名时发生SQL错误: {e}")
            return []
        finally:
            cursor.close()

    # 获取列
    def get_columns(self):
        return self._execute_in_queue(self._get_columns)

    # 检查制定的 group wxid 是否存在
    def check_group_exists(self, group_wxid):
        return self._execute_in_queue(self._check_group_exists, group_wxid)

    def _check_group_exists(self, group_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("""
                SELECT 1 FROM CHATROOMDATA 
                WHERE GROUP_WXID=? 
                LIMIT 1
            """, (group_wxid,))
            result = cursor.fetchone()
            return bool(result)
        except sqlite3.Error as e:
            logger.error(f"检查群组存在时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()