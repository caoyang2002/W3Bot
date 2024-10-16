import sqlite3
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

class ChatroomDatabase:
    def __init__(self, db_path="chatroomdata.db"):
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="chatroomdb")
        self._init_database()

    def _init_database(self):
        if not os.path.exists(self.db_path):
            logger.info(f"创建新的数据库: {self.db_path}")
            self._create_tables()
        else:
            logger.info(f"使用现有数据库: {self.db_path}")

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CHATROOMDATA (
                    GROUP_WXID TEXT,
                    USER_WXID TEXT,
                    USERNAME TEXT,
                    MESSAGE_CONTENT TEXT,
                    MESSAGE_TIMESTAMP TEXT,
                    MESSAGE_TYPE TEXT,
                    PRIMARY KEY (GROUP_WXID, USER_WXID)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS GROUPS (
                    GROUP_WXID TEXT PRIMARY KEY,
                    GROUP_NAME TEXT
                )
            """)
            conn.commit()

    def _execute_in_queue(self, method, *args, **kwargs):
        future = self.executor.submit(method, *args, **kwargs)
        try:
            return future.result(timeout=20)
        except Exception as error:
            logger.error(f"数据库操作错误: {error}")
            return None

    def get_group_info(self, group_wxid):
        return self._execute_in_queue(self._get_group_info, group_wxid)

    def _get_group_info(self, group_wxid):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM GROUPS WHERE GROUP_WXID=?", (group_wxid,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"获取群组信息时发生SQL错误: {e}")
            return None

    def create_group(self, group_wxid, group_name):
        return self._execute_in_queue(self._create_group, group_wxid, group_name)

    def _create_group(self, group_wxid, group_name):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO GROUPS (GROUP_WXID, GROUP_NAME) VALUES (?, ?)", 
                               (group_wxid, group_name))
                conn.commit()
            logger.info(f"群组已创建或更新: {group_wxid}, {group_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"创建群组时发生SQL错误: {e}")
            return False

    def add_message(self, group_wxid, user_wxid, username, content, msg_type):
        return self._execute_in_queue(self._add_message, group_wxid, user_wxid, username, content, msg_type)

    def _add_message(self, group_wxid, user_wxid, username, content, msg_type):
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO CHATROOMDATA 
                    (GROUP_WXID, USER_WXID, USERNAME, MESSAGE_CONTENT, MESSAGE_TIMESTAMP, MESSAGE_TYPE)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (group_wxid, user_wxid, username, content, current_time, msg_type))
                conn.commit()
            logger.info(f"消息已添加: {group_wxid}, {user_wxid}")
            return True
        except sqlite3.Error as e:
            logger.error(f"添加消息时发生SQL错误: {e}")
            return False

    def get_user_data(self, group_wxid, user_wxid):
        return self._execute_in_queue(self._get_user_data, group_wxid, user_wxid)

    def _get_user_data(self, group_wxid, user_wxid):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM CHATROOMDATA 
                    WHERE GROUP_WXID=? AND USER_WXID=?
                """, (group_wxid, user_wxid))
                data = cursor.fetchone()
                if data:
                    logger.debug(f"Raw user data: {data}")
                    logger.debug(f"Number of fields: {len(data)}")
                return data
        except sqlite3.Error as e:
            logger.error(f"获取用户数据时发生SQL错误: {e}")
            return None