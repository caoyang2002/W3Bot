# 查询语句

查看数据库
```bash
python3 ./help/sqlite.py chatroomdata.db "SELECT * FROM USERS LIMIT 5"
```

查看特定群组的用户
```bash
python3 sqlite.py chatroomdata.db "SELECT USER_WXID, USERNAME FROM CHATROOMDATA WHERE GROUP_WXID='58164277337@chatroom'"
```

查看最近的10条消息：

```bash
python sqlite_query.py chatroomdata.db "SELECT USERNAME, MESSAGE_CONTENT, MESSAGE_TIMESTAMP FROM CHATROOMDATA ORDER BY MESSAGE_TIMESTAMP DESC LIMIT 10"
```

查看白名单用户：

```bash
python sqlite_query.py chatroomdata.py "SELECT USERNAME, USER_WXID FROM CHATROOMDATA WHERE IS_WHITELIST=1"
```

统计每个群组的用户数量：

```bash
python sqlite_query.py chatroomdata.db "SELECT GROUP_WXID, COUNT(DISTINCT USER_WXID) as USER_COUNT FROM CHATROOMDATA GROUP BY GROUP_WXID"
```
