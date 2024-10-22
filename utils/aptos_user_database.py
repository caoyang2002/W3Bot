import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from utils.singleton import singleton

@singleton
class AptosUserDatabase:
    def __init__(self, db_path="aptosuserdata.db"):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            logger.warning("检测到用户数据库不存在，正在创建数据库")
            self._create_database()

        self.database = sqlite3.connect(self.db_path, check_same_thread=False)
        self.database.execute("PRAGMA foreign_keys = ON")
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="userdb")

    def _create_database(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.text_factory = str
        conn.execute("PRAGMA encoding = 'UTF-8';")
        c = conn.cursor()

        # 创建用户表
        c.execute("""
            CREATE TABLE USERS (
                USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NICKNAME TEXT,
                WXID TEXT UNIQUE,
                GROUP_IDS TEXT,  -- 存储为JSON数组
                WALLET_ADDRESS TEXT,
                GITHUB_ID TEXT,
                GOOGLE_ID TEXT,
                BALANCE REAL DEFAULT 0.0,
                JOIN_TIME TEXT,
                LAST_UPDATED TEXT
            )
        """)

        conn.commit()
        c.close()
        conn.close()
        logger.warning("已创建用户数据库")

    def _execute_in_queue(self, method, *args, **kwargs):
        future = self.executor.submit(method, *args, **kwargs)
        try:
            return future.result(timeout=20)
        except Exception as error:
            logger.error(f"数据库操作错误: {error}")
            return None

    def add_or_update_user(self, user_data: Dict[str, Any]) -> bool:
        return self._execute_in_queue(self._add_or_update_user, user_data)

    def _add_or_update_user(self, user_data: Dict[str, Any]) -> bool:
        cursor = self.database.cursor()
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            wxid = user_data.get('wxid')
            
            if 'group_ids' in user_data and isinstance(user_data['group_ids'], list):
                user_data['group_ids'] = json.dumps(user_data['group_ids'])

            cursor.execute("SELECT USER_ID FROM USERS WHERE WXID = ?", (wxid,))
            existing_user = cursor.fetchone()

            if existing_user:
                # 更新现有用户
                update_fields = []
                update_values = []
                
                for key, value in user_data.items():
                    if key.lower() != 'wxid' and value is not None:  # 不更新wxid
                        update_fields.append(f"{key.upper()} = ?")
                        update_values.append(value)
                
                update_fields.append("LAST_UPDATED = ?")
                update_values.extend([current_time, wxid])
                
                update_query = f"""
                    UPDATE USERS 
                    SET {', '.join(update_fields)}
                    WHERE WXID = ?
                """
                cursor.execute(update_query, update_values)
            else:
                # 插入新用户
                user_data['join_time'] = current_time
                user_data['last_updated'] = current_time
                
                fields = ['WXID'] + [key.upper() for key in user_data.keys() if key.lower() != 'wxid']
                values = [wxid] + [user_data[key] for key in user_data.keys() if key.lower() != 'wxid']
                
                insert_query = f"""
                    INSERT INTO USERS ({', '.join(fields)})
                    VALUES ({', '.join(['?' for _ in fields])})
                """
                cursor.execute(insert_query, values)

            self.database.commit()
            logger.info(f"用户数据已{'更新' if existing_user else '添加'}: {wxid}")
            return True

        except sqlite3.Error as e:
            logger.error(f"操作用户数据时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    def get_user_data(self, wxid: str) -> Optional[Dict[str, Any]]:
        return self._execute_in_queue(self._get_user_data, wxid)

    def _get_user_data(self, wxid: str) -> Optional[Dict[str, Any]]:
        cursor = self.database.cursor()
        try:
            cursor.execute("SELECT * FROM USERS WHERE WXID = ?", (wxid,))
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            
            if row:
                user_data = dict(zip(columns, row))
                # 将JSON字符串转换回列表
                if 'GROUP_IDS' in user_data and user_data['GROUP_IDS']:
                    user_data['GROUP_IDS'] = json.loads(user_data['GROUP_IDS'])
                return user_data
            return None

        except sqlite3.Error as e:
            logger.error(f"获取用户数据时发生SQL错误: {e}")
            return None
        finally:
            cursor.close()

    def update_user_field(self, wxid: str, field: str, value: Any) -> bool:
        return self._execute_in_queue(self._update_user_field, wxid, field, value)

    def _update_user_field(self, wxid: str, field: str, value: Any) -> bool:
        cursor = self.database.cursor()
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if field.upper() == 'GROUP_IDS' and isinstance(value, list):
                value = json.dumps(value)
            
            cursor.execute(f"""
                UPDATE USERS 
                SET {field.upper()} = ?, LAST_UPDATED = ?
                WHERE WXID = ?
            """, (value, current_time, wxid))
            
            self.database.commit()
            logger.info(f"用户 {wxid} 的 {field} 已更新为 {value}")
            return True

        except sqlite3.Error as e:
            logger.error(f"更新用户字段时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    def update_balance(self, wxid: str, amount: float, is_increment: bool = True) -> bool:
        return self._execute_in_queue(self._update_balance, wxid, amount, is_increment)

    def _update_balance(self, wxid: str, amount: float, is_increment: bool = True) -> bool:
        cursor = self.database.cursor()
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if is_increment:
                cursor.execute("""
                    UPDATE USERS 
                    SET BALANCE = BALANCE + ?, LAST_UPDATED = ?
                    WHERE WXID = ?
                """, (amount, current_time, wxid))
            else:
                cursor.execute("""
                    UPDATE USERS 
                    SET BALANCE = ?, LAST_UPDATED = ?
                    WHERE WXID = ?
                """, (amount, current_time, wxid))
            
            self.database.commit()
            logger.info(f"用户 {wxid} 的余额已{'增加' if is_increment else '更新为'} {amount}")
            return True

        except sqlite3.Error as e:
            logger.error(f"更新用户余额时发生SQL错误: {e}")
            return False
        finally:
            cursor.close()

    def get_users_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        return self._execute_in_queue(self._get_users_by_group, group_id)

    def _get_users_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        cursor = self.database.cursor()
        try:
            cursor.execute("""
                SELECT * FROM USERS 
                WHERE GROUP_IDS LIKE ?
            """, (f'%{group_id}%',))
            
            columns = [description[0] for description in cursor.description]
            users = []
            
            for row in cursor.fetchall():
                user_data = dict(zip(columns, row))
                if 'GROUP_IDS' in user_data and user_data['GROUP_IDS']:
                    user_data['GROUP_IDS'] = json.loads(user_data['GROUP_IDS'])
                users.append(user_data)
                
            return users

        except sqlite3.Error as e:
            logger.error(f"获取群组用户时发生SQL错误: {e}")
            return []
        finally:
            cursor.close()

    def __del__(self):
        self.database.close()
        self.executor.shutdown(wait=True)