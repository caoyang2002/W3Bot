import sqlite3
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from utils.singleton import singleton


@singleton
class ChatroomDatabase:
    def __init__(self):
        if not os.path.exists("chatroomdata.db"):
            logger.warning("检测到聊天室数据库不存在，正在创建数据库")
            conn = sqlite3.connect("chatroomdata.db")
            c = conn.cursor()
            c.execute("""CREATE TABLE GROUPINFO (
                GROUP_WXID TEXT PRIMARY KEY,
                GROUP_NAME TEXT
            )""")
            c.execute("""CREATE TABLE CHATROOMDATA (
                GROUP_WXID TEXT,
                USER_WXID TEXT,
                USERNAME TEXT,
                MESSAGE_CONTENT TEXT,
                MESSAGE_TIMESTAMP TEXT,
                MESSAGE_TYPE TEXT,
                JOIN_TIME TEXT,
                NICKNAME_CHANGE_COUNT INT,
                IS_WHITELIST INT,
                IS_BLACKLIST INT,
                IS_WARNED INT,
                BOT_CONFIDENCE REAL,
                DAILY_MESSAGE_COUNT INT,
                PRIMARY KEY (GROUP_WXID, USER_WXID),
                FOREIGN KEY (GROUP_WXID) REFERENCES GROUPINFO(GROUP_WXID)
            )""")
            conn.commit()
            c.close()
            conn.close()
            logger.warning("已创建聊天室数据库")

        self.database = sqlite3.connect(
            "chatroomdata.db", check_same_thread=False)
        self.executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="chatroomdb")

    def _execute_in_queue(self, method, *args, **kwargs):
        future = self.executor.submit(method, *args, **kwargs)
        try:
            return future.result(timeout=20)
        except Exception as error:
            logger.error(error)

    # 群组管理方法
    def create_group(self, group_wxid, group_name):
        return self._execute_in_queue(self._create_group, group_wxid, group_name)

    def _create_group(self, group_wxid, group_name):
        cursor = self.database.cursor()
        try:
            cursor.execute("INSERT INTO GROUPINFO (GROUP_WXID, GROUP_NAME) VALUES (?, ?)",
                           (group_wxid, group_name))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已创建群组: {group_wxid}, {group_name}")
        finally:
            cursor.close()

    def update_group_name(self, group_wxid, new_group_name):
        return self._execute_in_queue(self._update_group_name, group_wxid, new_group_name)

    def _update_group_name(self, group_wxid, new_group_name):
        cursor = self.database.cursor()
        try:
            cursor.execute(
                "UPDATE GROUPINFO SET GROUP_NAME=? WHERE GROUP_WXID=?", (new_group_name, group_wxid))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已更新群组名称: {group_wxid}, {new_group_name}")
        finally:
            cursor.close()

    def delete_group(self, group_wxid):
        return self._execute_in_queue(self._delete_group, group_wxid)

    def _delete_group(self, group_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute(
                "DELETE FROM GROUPINFO WHERE GROUP_WXID=?", (group_wxid,))
            cursor.execute(
                "DELETE FROM CHATROOMDATA WHERE GROUP_WXID=?", (group_wxid,))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已删除群组及其所有数据: {group_wxid}")
        finally:
            cursor.close()

    def get_group_info(self, group_wxid):
        return self._execute_in_queue(self._get_group_info, group_wxid)

    def _get_group_info(self, group_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute(
                "SELECT * FROM GROUPINFO WHERE GROUP_WXID=?", (group_wxid,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_all_groups(self):
        return self._execute_in_queue(self._get_all_groups)

    def _get_all_groups(self):
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT * FROM GROUPINFO")
            return cursor.fetchall()
        finally:
            cursor.close()

    # 用户管理方法
    def _check_user(self, group_wxid, user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute(
                "SELECT * FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?", (group_wxid, user_wxid))
            if not cursor.fetchone():
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO CHATROOMDATA 
                    (GROUP_WXID, USER_WXID, JOIN_TIME, NICKNAME_CHANGE_COUNT, IS_WHITELIST, IS_BLACKLIST, IS_WARNED, BOT_CONFIDENCE, DAILY_MESSAGE_COUNT)
                    VALUES (?, ?, ?, 0, 0, 0, 0, 0.0, 0)
                """, (group_wxid, user_wxid, current_time))
                self.database.commit()
        finally:
            cursor.close()

    def add_message(self, group_wxid, user_wxid, username, content, msg_type):
        return self._execute_in_queue(self._add_message, group_wxid, user_wxid, username, content, msg_type)

    def _add_message(self, group_wxid, user_wxid, username, content, msg_type):
        cursor = self.database.cursor()
        try:
            self._check_user(group_wxid, user_wxid)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE CHATROOMDATA 
                SET USERNAME=?, MESSAGE_CONTENT=?, MESSAGE_TIMESTAMP=?, MESSAGE_TYPE=?, DAILY_MESSAGE_COUNT = DAILY_MESSAGE_COUNT + 1
                WHERE GROUP_WXID=? AND USER_WXID=?
            """, (username, content, timestamp, msg_type, group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已添加消息: {group_wxid}, {
                        user_wxid}, {username}")
        finally:
            cursor.close()

    def increment_nickname_change_count(self, group_wxid, user_wxid):
        return self._execute_in_queue(self._increment_nickname_change_count, group_wxid, user_wxid)

    def _increment_nickname_change_count(self, group_wxid, user_wxid):
        cursor = self.database.cursor()
        try:
            self._check_user(group_wxid, user_wxid)
            cursor.execute("""
                UPDATE CHATROOMDATA 
                SET NICKNAME_CHANGE_COUNT = NICKNAME_CHANGE_COUNT + 1 
                WHERE GROUP_WXID=? AND USER_WXID=?
            """, (group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已增加昵称修改次数: {group_wxid}, {user_wxid}")
        finally:
            cursor.close()

    def set_whitelist(self, group_wxid, user_wxid, status):
        return self._execute_in_queue(self._set_whitelist, group_wxid, user_wxid, status)

    def _set_whitelist(self, group_wxid, user_wxid, status):
        cursor = self.database.cursor()
        try:
            self._check_user(group_wxid, user_wxid)
            cursor.execute(
                "UPDATE CHATROOMDATA SET IS_WHITELIST=? WHERE GROUP_WXID=? AND USER_WXID=?", (status, group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已设置白名单状态: {
                        group_wxid}, {user_wxid}, {status}")
        finally:
            cursor.close()

    def set_blacklist(self, group_wxid, user_wxid, status):
        return self._execute_in_queue(self._set_blacklist, group_wxid, user_wxid, status)

    def _set_blacklist(self, group_wxid, user_wxid, status):
        cursor = self.database.cursor()
        try:
            self._check_user(group_wxid, user_wxid)
            cursor.execute(
                "UPDATE CHATROOMDATA SET IS_BLACKLIST=? WHERE GROUP_WXID=? AND USER_WXID=?", (status, group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已设置黑名单状态: {
                        group_wxid}, {user_wxid}, {status}")
        finally:
            cursor.close()

    def set_warned(self, group_wxid, user_wxid, status):
        return self._execute_in_queue(self._set_warned, group_wxid, user_wxid, status)

    def _set_warned(self, group_wxid, user_wxid, status):
        cursor = self.database.cursor()
        try:
            self._check_user(group_wxid, user_wxid)
            cursor.execute(
                "UPDATE CHATROOMDATA SET IS_WARNED=? WHERE GROUP_WXID=? AND USER_WXID=?", (status, group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已设置警告状态: {group_wxid}, {
                        user_wxid}, {status}")
        finally:
            cursor.close()

    def update_bot_confidence(self, group_wxid, user_wxid, confidence):
        return self._execute_in_queue(self._update_bot_confidence, group_wxid, user_wxid, confidence)

    def _update_bot_confidence(self, group_wxid, user_wxid, confidence):
        cursor = self.database.cursor()
        try:
            self._check_user(group_wxid, user_wxid)
            cursor.execute("UPDATE CHATROOMDATA SET BOT_CONFIDENCE=? WHERE GROUP_WXID=? AND USER_WXID=?",
                           (confidence, group_wxid, user_wxid))
            self.database.commit()
            logger.info(f"[聊天室数据库] 已更新机器人置信度: {group_wxid}, {
                        user_wxid}, {confidence}")
        finally:
            cursor.close()

    def get_user_stats(self, user_wxid):
        return self._execute_in_queue(self._get_user_stats, user_wxid)

    def _get_user_stats(self, user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute("""
                SELECT GROUP_WXID, NICKNAME_CHANGE_COUNT, DAILY_MESSAGE_COUNT
                FROM CHATROOMDATA
                WHERE USER_WXID=?
            """, (user_wxid,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def reset_daily_message_count(self):
        return self._execute_in_queue(self._reset_daily_message_count)

    def _reset_daily_message_count(self):
        cursor = self.database.cursor()
        try:
            cursor.execute("UPDATE CHATROOMDATA SET DAILY_MESSAGE_COUNT = 0")
            self.database.commit()
            logger.info("[聊天室数据库] 已重置所有用户的每日消息计数")
        finally:
            cursor.close()

    def get_user_data(self, group_wxid, user_wxid):
        return self._execute_in_queue(self._get_user_data, group_wxid, user_wxid)

    def _get_user_data(self, group_wxid, user_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute(
                "SELECT * FROM CHATROOMDATA WHERE GROUP_WXID=? AND USER_WXID=?", (group_wxid, user_wxid))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_group_users(self, group_wxid):
        return self._execute_in_queue(self._get_group_users, group_wxid)

    def _get_group_users(self, group_wxid):
        cursor = self.database.cursor()
        try:
            cursor.execute(
                "SELECT * FROM CHATROOMDATA WHERE GROUP_WXID=?", (group_wxid,))
            return cursor.fetchall()
        finally:
            cursor.close()
