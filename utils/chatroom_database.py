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

    def _execute_in_queue(self, method, *args, **kwargs):
        future = self.executor.submit(method, *args, **kwargs)
        try:
            return future.result(timeout=20)
        except Exception as error:
            logger.error(f"数据库操作错误: {error}")
            return None

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

    def add_or_update_user(self, group_wxid, user_wxid, username, message_content, message_type):
        return self._execute_in_queue(self._add_or_update_user, group_wxid, user_wxid, username, message_content, message_type)

    def _add_or_update_user(self, group_wxid, user_wxid, username, message_content, message_type):
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO CHATROOMDATA 
                    (GROUP_WXID, USER_WXID, USERNAME, MESSAGE_CONTENT, MESSAGE_TIMESTAMP, MESSAGE_TYPE, JOIN_TIME, 
                     NICKNAME_CHANGE_COUNT, IS_WHITELIST, IS_BLACKLIST, IS_WARNED, BOT_CONFIDENCE)
                    VALUES (?, ?, ?, ?, ?, ?, 
                            COALESCE((SELECT JOIN_TIME FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), ?),
                            COALESCE((SELECT NICKNAME_CHANGE_COUNT FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                            COALESCE((SELECT IS_WHITELIST FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                            COALESCE((SELECT IS_BLACKLIST FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                            COALESCE((SELECT IS_WARNED FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0),
                            COALESCE((SELECT BOT_CONFIDENCE FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?), 0.0))
                """, (group_wxid, user_wxid, username, message_content, current_time, message_type,
                      group_wxid, user_wxid, current_time,
                      group_wxid, user_wxid,
                      group_wxid, user_wxid,
                      group_wxid, user_wxid,
                      group_wxid, user_wxid,
                      group_wxid, user_wxid))
                conn.commit()
            logger.info(f"用户数据已添加或更新: {group_wxid}, {user_wxid}")
            return True
        except sqlite3.Error as e:
            logger.error(f"添加或更新用户数据时发生SQL错误: {e}")
            return False

    # 可以根据需要添加更多方法，如更新特定字段、删除用户等