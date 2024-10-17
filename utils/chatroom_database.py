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
            self._create_database()

        self.database = sqlite3.connect(self.db_path, check_same_thread=False)
        self.database.execute("PRAGMA foreign_keys = ON")
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="chatroomdb")

    def _create_database(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.text_factory = str
        conn.execute("PRAGMA encoding = 'UTF-8';")
        c = conn.cursor()

        c.execute("""
            CREATE TABLE USERS (
                USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_WXID TEXT UNIQUE,
                JOIN_TIME TEXT,
                IS_WHITELIST INTEGER,
                IS_BLACKLIST INTEGER,
                IS_WARNED INTEGER,
                BOT_CONFIDENCE REAL
            )
        """)

        c.execute("""
            CREATE TABLE MESSAGES (
                MESSAGE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID INTEGER,
                GROUP_WXID TEXT,
                USERNAME TEXT COLLATE NOCASE,
                MESSAGE_CONTENT TEXT COLLATE NOCASE,
                MESSAGE_TIMESTAMP TEXT,
                MESSAGE_TYPE TEXT,
                FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID)
            )
        """)

        conn.commit()
        c.close()
        conn.close()
        logger.warning("已创建聊天室数据库")

    # 安全执行
    def _execute_in_queue(self, method, *args, **kwargs):
        future = self.executor.submit(method, *args, **kwargs)
        try:
            return future.result(timeout=20)
        except Exception as error:
            logger.error(f"数据库操作错误: {error}")
            return None

    def add_message(self, group_wxid, user_wxid, username, content, msg_type):
        return self._execute_in_queue(self._add_message, group_wxid, user_wxid, username, content, msg_type)

    def _add_message(self, group_wxid, user_wxid, username, content, msg_type):
        cursor = self.database.cursor()
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            group_wxid = str(group_wxid) if group_wxid is not None else ""
            user_wxid = str(user_wxid) if user_wxid is not None else ""
            username = str(username) if username is not None else ""
            content = str(content) if content is not None else ""
            msg_type = str(msg_type) if msg_type is not None else ""

            cursor.execute("SELECT USER_ID FROM USERS WHERE USER_WXID = ?", (user_wxid,))
            user = cursor.fetchone()
            if user is None:
                cursor.execute("""
                    INSERT INTO USERS (USER_WXID, JOIN_TIME, IS_WHITELIST, IS_BLACKLIST, IS_WARNED, BOT_CONFIDENCE)
                    VALUES (?, ?, 0, 0, 0, 0.0)
                """, (user_wxid, current_time))
                user_id = cursor.lastrowid
            else:
                user_id = user[0]

            cursor.execute("""
                INSERT INTO MESSAGES (USER_ID, GROUP_WXID, USERNAME, MESSAGE_CONTENT, MESSAGE_TIMESTAMP, MESSAGE_TYPE)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, group_wxid, username, content, current_time, msg_type))

            self.database.commit()
            logger.info(f"新消息已添加: {group_wxid}, {user_wxid}")
            return True
        except sqlite3.Error as e:
            logger.error(f"添加新消息时发生SQL错误: {e}")
            logger.error(f"错误的参数: group_wxid={group_wxid}, user_wxid={user_wxid}, username={username}, content={content}, msg_type={msg_type}")
            return False
        finally:
            cursor.close()

    # 获取用户数据
    def get_user_data(self, group_wxid,user_wxid):
        return self._execute_in_queue(self._get_user_data, user_wxid)

    def _get_user_data(self, user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT * FROM USERS WHERE USER_WXID = ?", (user_wxid,))
            data = cursor.fetchone()
            if data:
                logger.debug(f"原始用户数据: {data}")
            return data
        except sqlite3.Error as e:
            logger.error(f"获取用户数据时发生SQL错误: {e}")
            return None
        finally:
            cursor.close()



    def set_whitelist(self, user_wxid, status):
        return self._execute_in_queue(self._set_whitelist, user_wxid, status)

    def _set_whitelist(self, user_wxid, status):
        cursor = self.database.cursor()
        try:
            cursor.execute("UPDATE USERS SET IS_WHITELIST = ? WHERE USER_WXID = ?", (status, user_wxid))
            self.database.commit()
            logger.info(f"[数据库] {user_wxid} 白名单状态已设置为 {status}")
            return True
        except sqlite3.Error as e:
            logger.error(f"设置白名单状态时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    def get_whitelist(self, user_wxid):
        return self._execute_in_queue(self._get_whitelist, user_wxid)

    def _get_whitelist(self, user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT IS_WHITELIST FROM USERS WHERE USER_WXID = ?", (user_wxid,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"获取白名单状态时发生SQL错误: {e}")
            return None
        finally:
            cursor.close()

    def get_user_messages(self, user_wxid, group_wxid=None, limit=100):
        return self._execute_in_queue(self._get_user_messages, user_wxid, group_wxid, limit)

    def _get_user_messages(self, user_wxid, group_wxid=None, limit=100):
        cursor = self.database.cursor()
        try:
            if group_wxid:
                cursor.execute("""
                    SELECT M.* FROM MESSAGES M
                    JOIN USERS U ON M.USER_ID = U.USER_ID
                    WHERE U.USER_WXID = ? AND M.GROUP_WXID = ?
                    ORDER BY M.MESSAGE_TIMESTAMP DESC
                    LIMIT ?
                """, (user_wxid, group_wxid, limit))
            else:
                cursor.execute("""
                    SELECT M.* FROM MESSAGES M
                    JOIN USERS U ON M.USER_ID = U.USER_ID
                    WHERE U.USER_WXID = ?
                    ORDER BY M.MESSAGE_TIMESTAMP DESC
                    LIMIT ?
                """, (user_wxid, limit))
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"获取用户消息时发生SQL错误: {e}")
            return []
        finally:
            cursor.close()

    def get_user_list(self, group_wxid=None):
        return self._execute_in_queue(self._get_user_list, group_wxid)

    def _get_user_list(self, group_wxid=None):
        cursor = self.database.cursor()
        try:
            if group_wxid:
                cursor.execute("""
                    SELECT DISTINCT U.* FROM USERS U
                    JOIN MESSAGES M ON U.USER_ID = M.USER_ID
                    WHERE M.GROUP_WXID = ?
                """, (group_wxid,))
            else:
                cursor.execute("SELECT * FROM USERS")
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"获取用户列表时发生SQL错误: {e}")
            return []
        finally:
            cursor.close()

    def get_user_count(self, group_wxid=None):
        return self._execute_in_queue(self._get_user_count, group_wxid)

    def _get_user_count(self, group_wxid=None):
        cursor = self.database.cursor()
        try:
            if group_wxid:
                cursor.execute("""
                    SELECT COUNT(DISTINCT U.USER_ID) FROM USERS U
                    JOIN MESSAGES M ON U.USER_ID = M.USER_ID
                    WHERE M.GROUP_WXID = ?
                """, (group_wxid,))
            else:
                cursor.execute("SELECT COUNT(*) FROM USERS")
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"获取用户数量时发生SQL错误: {e}")
            return 0
        finally:
            cursor.close()

# 通过用户 wxid 获取用户发送的消息
    def get_messages_by_user_wxid(self,user_wxid):
        return self._execute_in_queue(self._get_messages_by_user_wxid, user_wxid)
    def _get_messages_by_user_wxid(self,user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT * FROM MESSAGES WHERE USER_ID = ?", (user_wxid,))
            messages = cursor.fetchall()
            return messages
        except sqlite3.Error as e:
            logger.error(f"获取用户消息时发生SQL错误: {e}")
            return 0
        finally:
            cursor.close()



    # 检查群组是否存在

    def check_group_exists(self, group_wxid):
        return self._execute_in_queue(self._check_group_exists, group_wxid)

    def _check_group_exists(self, group_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT 1 FROM MESSAGES WHERE GROUP_WXID = ? LIMIT 1", (group_wxid,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"检查群组存在时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    def add_column(self, table_name, column_name: str, column_type: str):
        return self._execute_in_queue(self._add_column, table_name, column_name, column_type)

    def _add_column(self, table_name, column_name: str, column_type: str):
        cursor = self.database.cursor()
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            self.database.commit()
            logger.info(f"[数据库] 已添加列 {column_name} 到表 {table_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"添加列时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    def get_columns(self, table_name):
        return self._execute_in_queue(self._get_columns, table_name)

    def _get_columns(self, table_name):
        cursor = self.database.cursor()
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            return column_names
        except sqlite3.Error as e:
            logger.error(f"获取列名时发生SQL错误: {e}")
            return []
        finally:
            cursor.close()

    def __del__(self):
        self.database.close()
        self.executor.shutdown(wait=True)
