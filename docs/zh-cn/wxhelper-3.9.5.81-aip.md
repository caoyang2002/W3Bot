# wxhelper API 文档

[toc]

> 3.9.5.81 版本，http 接口文档，文档仅供参考。

所有接口只支持 `post` 方法。

全部使用 `json` 格式。

格式： http://host:port/api/xxxx

host: 绑定的host

port: 监听的端口

xxxx: 对应的功能路径

返回结构的 json 格式：

 ``` javascript
  {
    "code": 1,
    "data": {},
    "msg": "success"
}
 ```

code： 错误码

msg：  成功/错误信息

data： 接口返回的数据


## 1. 检查微信登录

### 接口功能

> 检查微信是否登录

### 接口地址

> `/api/checkLogin`

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|


### 返回字段

|返回字段|字段类型|说明                              |
|:--|:--|:--|
|code|int|返回状态,1 成功, 0失败|
|result|string|成功提示|
|data|string|响应内容|

### 接口示例
入参：
``` javascript
```
响应：
``` javascript
{
    "code": 1,
    "msg": "success",
    "data":null
}
```

## 2.获取登录用户信息

### 接口功能

> 获取登录用户信息

### 接口地址

> `/api/userInfo`

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|


### 返回字段

|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1 成功, 0失败|
|result|string|成功提示|
|data|object|响应内容|
|account|string|账号|
|headImage|string|头像|
|city|string|城市|
|country|string|国家|
|currentDataPath|string|当前数据目录,登录的账号目录|
|dataSavePath|string|微信保存目录|
|mobile|string|手机|
|name|string|昵称|
|province|string|省|
|wxid|string|wxid|
|signature|string|个人签名|
|dbKey|string|数据库的SQLCipher的加密key，可以使用该key配合decrypt.py解密数据库

### 接口示例
入参：
``` javascript
```
响应：
``` javascript
{
    "code": 1,
    "data": {
        "account": "xxx",
        "city": "Zhengzhou",
        "country": "CN",
        "currentDataPath": "C:\\WeChat Files\\wxid_xxx\\",
        "dataSavePath": "C:\\wechatDir\\WeChat Files\\",
        "dbKey": "965715e30e474da09250cb5aa047e3940ffa1c8f767c4263b132bb512933db49",
        "headImage": "https://wx.qlogo.cn/mmhead/ver_1/MiblV0loY0GILewQ4u2121",
        "mobile": "13949175447",
        "name": "xxx",
        "province": "Henan",
        "signature": "xxx",
        "wxid": "wxid_22222"
    },
    "msg": "success"
}
```



## 2.发送文本消息

### 接口功能

> 发送文本消息

### 接口地址

> [/api/sendTextMsg](/api/sendTextMsg)

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|
|wxid |true |string| 接收人wxid |
|msg|true |string|消息文本内容|

### 返回字段

|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,不为0成功, 0失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{
    "wxid": "filehelper",
    "msg": "1112222"
}
```
响应：
``` javascript
{"code":345686720,"msg":"success","data":null}
```

## 3.hook消息

### 接口功能

> hook接收文本消息，图片消息，群消息.该接口将hook的消息通过tcp回传给本地的端口。
> enableHttp=1时，使用url，timeout参数配置服务端的接收地址。请求为post，Content-Type 为json。
> enableHttp=0时，使用ip，port的tcp服务回传消息。

### 接口地址

> `/api/hookSyncMsg`

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|
|port |true |string| 本地服务端端口，用来接收消息内容 |
|ip |true |string| 服务端ip地址，用来接收消息内容，可以是任意ip,即tcp客户端连接的服务端的ip|
|url |true |string| http的请求地址，enableHttp=1时，不能为空 |
|timeout |true |string| 超时时间，单位ms|
|enableHttp |true |number| 0/1 ：1.启用http 0.不启用http|

### 返回字段

|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, 非0失败|
|data|object|null|
|msg|string|成功提示|


### 接口示例

入参：
``` javascript
{
    "port": "19099",
    "ip":"127.0.0.1",
    "url":"http://localhost:8080",
    "timeout":"3000",
    "enableHttp":"0"
}
```
响应：
``` javascript
{"code":0,"msg":"success","data":null}
```

## 4.取消hook消息

### 接口功能

> 取消hook消息

### 接口地址

> /api/unhookSyncMsg

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|


### 返回字段

|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, 非0失败|
|data|object|null|
|msg|string|成功提示|


### 接口示例

入参：

``` javascript

```

响应：

``` javascript
{"code":0,"msg":"success","data":null}
```

## 5.好友列表

### 接口功能

> 好友列表

### 接口地址

> `/api/getContactList`

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|


### 返回字段

|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, 非0失败|
|data|object|好友信息|
|customAccount|string|自定义账号|
|encryptName|string|昵称|
|nickname|string|昵称|
|pinyin|string|简拼|
|pinyinAll|string|全拼|
|reserved1|number|未知|
|reserved2|number|未知|
|type|number|未知|
|verifyFlag|number|未知|
|wxid|string|wxid|
|msg|string|成功提示|


### 接口示例

入参：

``` javascript

```

响应：

``` javascript
{
    "code": 1,
    "data": [
        {
           "customAccount": "",
            "encryptName": "v3_020b3826fd03010000000000e04128fddf4d90000000501ea9a3dba12f95f6b60a0536a1adb6b40fc4086288f46c0b89e6c4eb8062bb1661b4b6fbab708dc4f89d543d7ade135b2be74c14b9cfe3accef377b9@stranger",
            "nickname": "文件传输助手",
            "pinyin": "WJCSZS",
            "pinyinAll": "wenjianchuanshuzhushou",
            "reserved1": 1,
            "reserved2": 1,
            "type": 3,
            "verifyFlag": 0,
            "wxid": "filehelper"
        }
    ].
    "msg": "success"
```

## 6.获取数据库信息

### 接口功能

> 获取数据库信息和句柄

### 接口地址

> `/api/getDBInfo`

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|


### 返回字段

|返回字段|字段类型|说明|
|---|---|---|
|code|int|返回状态,0成功, 非0失败|
|msg|string|返回信息|
|data|array|好友信息|
|databaseName|string|数据库名称|
|handle|number|句柄|
|tables|array|表信息|
|name|string|表名|
|rootpage|string|rootpage|
|sql|string|ddl语句|
|tableName|string|表名|


### 接口示例

入参：

``` javascript

```

响应：

``` javascript
{
    "code": 1,
    "data": [
        {
            "databaseName": "MicroMsg.db",
            "handle": 1755003930784,
            "tables": [
                {
                    "name": "Contact",
                    "rootpage": "2",
                    "sql": "CREATE TABLE Contact(UserName TEXT PRIMARY KEY ,Alias TEXT,EncryptUserName TEXT,DelFlag INTEGER DEFAULT 0,Type INTEGER DEFAULT 0,VerifyFlag INTEGER DEFAULT 0,Reserved1 INTEGER DEFAULT 0,Reserved2 INTEGER DEFAULT 0,Reserved3 TEXT,Reserved4 TEXT,Remark TEXT,NickName TEXT,LabelIDList TEXT,DomainList TEXT,ChatRoomType int,PYInitial TEXT,QuanPin TEXT,RemarkPYInitial TEXT,RemarkQuanPin TEXT,BigHeadImgUrl TEXT,SmallHeadImgUrl TEXT,HeadImgMd5 TEXT,ChatRoomNotify INTEGER DEFAULT 0,Reserved5 INTEGER DEFAULT 0,Reserved6 TEXT,Reserved7 TEXT,ExtraBuf BLOB,Reserved8 INTEGER DEFAULT 0,Reserved9 INTEGER DEFAULT 0,Reserved10 TEXT,Reserved11 TEXT)",
                    "tableName": "Contact"
                }
            ]
        }
    ],
    "msg":"success"
}
```


## 7.查询数据库

### 接口功能

> 查询数据库

### 接口地址

> `/api/execSql`

### HTTP 请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|
|dbHandle |true |number|  |
|sql |true |string| 执行的sql |

### 返回字段

|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, 非0失败|
|msg|string|返回信息|
|data|array|sqlite返回的结果|



### 接口示例
入参：
``` javascript
{
    "dbHandle":2006119800400,
    "sql":"select * from MSG where localId =301;"
}
```

响应：

``` javascript
{
    "code": 1,
    "data": [
        [
            "localId",
            "TalkerId",
            "MsgSvrID",
            "Type",
            "SubType",
            "IsSender",
            "CreateTime",
            "Sequence",
            "StatusEx",
            "FlagEx",
            "Status",
            "MsgServerSeq",
            "MsgSequence",
            "StrTalker",
            "StrContent",
            "DisplayContent",
            "Reserved0",
            "Reserved1",
            "Reserved2",
            "Reserved3",
            "Reserved4",
            "Reserved5",
            "Reserved6",
            "CompressContent",
            "BytesExtra",
            "BytesTrans"
        ],
        [
            "301",
            "1",
            "8824834301214701891",
            "1",
            "0",
            "0",
            "1685401473",
            "1685401473000",
            "0",
            "0",
            "2",
            "1",
            "795781866",
            "wxid_123",
            "testtest",
            "",
            "0",
            "2",
            "",
            "",
            "",
            "",
            "",
            "",
            "CgQIEBAAGo0BCAcSiAE8bXNnc291cmNlPJPHNpZ25hdHVyZT52MV9wd12bTZyRzwvc2lnbmF0dXJPgoJPHRtcF9ub2RlPgoJCTxwsaXNoZXItaWQ+Jmx0OyFbQ0RBVEFbXV0mZ3Q7PC9wdWJsaXNoZXItaWQ+Cgk8L3RtcF9ub2RlPgo8L21zZ3NvdXJjZT4KGiQIAhIgNDE1MDA0NjRhZTRmMjk2NjhjMzY2ZjFkOTdmMjAwNDg=",
            ""
        ]
    ],
    "msg": "success"
}
```


## 8.发送文件消息

### 接口功能
> 发送文件消息

### 接口地址
> [/api/sendFileMsg](/api/sendFileMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid |true |string| 接收人wxid |
|filePath|true |string|文件绝对路径|

### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,不为0成功, 0失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript
{
    "wxid": "filehelper",
    "filePath": "c:\\test.zip"
}
```
响应：
``` javascript
{"code":345686720,"msg":"success","data":null}
```


## 9.获取群详情

### 接口功能

> 获取群详情

### 接口地址

> /api/getChatRoomDetailInfo

### HTTP请求方式

> POST  JSON

### 请求参数

|参数|必选|类型|说明|
|---|---|---|---|
|chatRoomId |true |string| 群id |


### 返回字段

|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|群详细内容|
|chatRoomId|string|群id|
|notice|string|公告通知|
|admin|string|群管理|
|xml|string|xml信息|

### 接口示例

入参：
``` javascript
{
    "chatRoomId": "12222@chatroom"
}
```
响应：
``` javascript
{"code":345686720,"msg":"success","data":{
    "chatRoomId":"12222@chatroom",
    "notice":"test",
    "admin":"wxid_122333",
    "xml":"",
}}
```


## 10. 添加群成员
### 接口功能
> 获取群详情

### 接口地址
> [/api/addMemberToChatRoom](/api/addMemberToChatRoom)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|chatRoomId |true |string| 群id |
|memberIds |true |string| 成员id，多个用,分隔 |

### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功,负数失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{
    "chatRoomId":"21363231004@chatroom",
    "memberIds":"wxid_oyb662qhop4422"
}
```
响应：
``` javascript
{"code":1,"msg":"success","data":null}
```


## 11.修改群昵称**
### 接口功能
> 修改群昵称

### 接口地址
> [/api/modifyNickname](/api/modifyNickname)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|chatRoomId |true |string| 群id |
|wxid |true |string| 自己的wxid |
|nickName |true |string| 昵称 |


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript

{
    "chatRoomId":"31004@chatroom",
    "wxid":"wxid_2721221512",
    "nickName":"1221"
}
```
响应：
``` javascript
{"code":1,"msg":"success","data":null}
```

## 12.删除群成员**
### 接口功能
> 删除群成员

### 接口地址
> [/api/delMemberFromChatRoom](/api/delMemberFromChatRoom)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|chatRoomId |true |string| 群id |
|memberIds |true |string| 成员id,用,分隔 |



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript

{
    "chatRoomId":"1234@chatroom",
    "memberIds":"wxid_123"
}
```
响应：
``` javascript
{"code":1,"msg":"success","data":null}
```


## 13.获取群成员**
### 接口功能
> 获取群成员

### 接口地址
> [/api/getMemberFromChatRoom](/api/getMemberFromChatRoom)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|chatRoomId |true |string| 群id |



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|
|chatRoomId|string|群id|
|members|string|成员id|
|memberNickname|string|成员昵称|
|admin|string|群管理|
|adminNickname|string|管理昵称|

### 接口示例

入参：
``` javascript

{
    "chatRoomId":"1234@chatroom"
}
```
响应：
``` javascript
{
    "code": 1,
    "data": {
        "admin": "wxid_2222",
        "adminNickname": "123",
        "chatRoomId": "22224@chatroom",
        "memberNickname": "^G123^G^G",
        "members": "wxid_2222^Gwxid_333"
    },
    "msg": "success"
}
```

## 14.置顶群消息**
### 接口功能
> 置顶群消息，需要群主权限

### 接口地址
> [/api/topMsg](/api/topMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|msgId |true |string| 消息id |



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript


{
    "msgId":8005736725060623215
}
```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```


## 15.移除置顶群消息**
### 接口功能
> 移除置顶群消息，需要群主权限

### 接口地址
> [/api/removeTopMsg](/api/removeTopMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|msgId |true |string| 消息id |
|chatRoomId |true |string| 群id |


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript


{
    "msgId":8005736725060623215,
     "chatRoomId":"12345678@chatroom"
}
```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```

## 16.邀请入群**
### 接口功能
> 邀请入群，（40人以上的群需要使用邀请入群）

### 接口地址
> [/api/InviteMemberToChatRoom](/api/InviteMemberToChatRoom)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|memberIds |true |string| wxid，用,分隔 |
|chatRoomId |true |string| 群id |


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript


{
    "memberIds":"wxid_123,wxid_12341",
     "chatRoomId":"12345678@chatroom"
}
```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```


## 17.hook日志**
### 接口功能
> hook微信日志，输出在wechat安装目录的logs目录下

### 接口地址
> [/api/hookLog](/api/hookLog)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript



```
响应：
``` javascript
{
    "code": 0,
    "data": null,
    "msg": "success"
}
```

## 18.取消hook日志**
### 接口功能
> 取消hook日志

### 接口地址
> [/api/unhookLog](/api/unhookLog)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript


```
响应：
``` javascript
{
    "code": 0,
    "data": null,
    "msg": "success"
}
```

## 19.建群**
### 接口功能
> 建群（不建议使用，容易被封，测试期间被封了，无法保证效果）

### 接口地址
> [/api/createChatRoom](/api/createChatRoom)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|memberIds|string|群成员id，以,分割|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript


```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```

## 20.退群**
### 接口功能
> 退群

### 接口地址
> [/api/quitChatRoom](/api/quitChatRoom)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|chatRoomId|string|群id|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{
    "chatRoomId":"123456@chatroom"
}

```
响应：
``` javascript
{
    "code": 119536579329,
    "data": null,
    "msg": "success"
}
```

## 21.转发消息**
### 接口功能
> 转发消息

### 接口地址
> [/api/forwardMsg](/api/forwardMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid|string|接收人id|
|msgId|string|消息id|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{
    "wxid":"filehelper",
    "msgId":"1233312233123"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```

## 22.朋友圈首页**
### 接口功能
> 朋友圈首页,前置条件需先调用hook消息接口成功,具体内容会在hook消息里返回，格式如下：
``` javascript
{
    "data":[
        {
            "content": "",
            "createTime': 1691125287,
            "senderId': "",
            "snsId': 123,
            "xml':""
        }
    ]
}
```

### 接口地址
> [/api/getSNSFirstPage](/api/getSNSFirstPage)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript


```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```

## 23.朋友圈下一页**
### 接口功能
> 朋友圈下一页

### 接口地址
> [/api/getSNSNextPage](/api/getSNSNextPage)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|snsId|number|snsId|



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{

    "snsid":123
}

```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```


## 24.收藏消息**
### 接口功能
> 收藏消息

### 接口地址
> [/api/addFavFromMsg](/api/addFavFromMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|msgId|number|消息id|



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{

    "msgId":123
}

```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```

## 24.收藏图片**
### 接口功能
> 收藏图片

### 接口地址
> [/api/addFavFromImage](/api/addFavFromImage)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid|string|wxid|
|imagePath|string|图片地址|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,1成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{

    "wxid":"wxid_12333",
    "imagePath":"C:\\test\\test.png"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": null,
    "msg": "success"
}
```

## 25.发送@消息**
### 接口功能
> 发送@消息

### 接口地址
> [/api/sendAtText](/api/sendAtText)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxids|string|wxid字符串，多个用,分隔，发送所有人传值"notify@all"|
|chatRoomId|string|群id|
|msg|string|消息内容|

### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|


### 接口示例

入参：
``` javascript
{

    "wxids":"notify@all",
    "chatRoomId":"123@chatroom",
    "msg":"你们好啊"

}

```
响应：
``` javascript
{
    "code": 67316444768,
    "data": null,
    "msg": "success"
}
```

## 26.获取群成员信息**
### 接口功能
> 获取群成员基础信息

### 接口地址
> [/api/getContactProfile](/api/getContactProfile)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid|string|wxid|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|
|account|string|账号|
|headImage|string|头像|
|nickname|string|昵称|
|v3|string|v3|
|wxid|string|wxid|

### 接口示例

入参：
``` javascript

{
    "wxid":"wxid_123"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {
        "account": "account",
        "headImage": "https://wx.qlogo.cn/mmhead/ver_1/0",
        "nickname": "test",
        "v3": "wxid_123",
        "wxid": "wxid_123"
    },
    "msg": "success"
}
```

## 27.发送公众号消息**
### 接口功能
> 自定义发送公众号消息

### 接口地址
> [/api/forwardPublicMsg](/api/forwardPublicMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|appName|string|公众号id，消息内容里的appname|
|userName|string|公众号昵称，消息内容里的username|
|title|string|链接地址，消息内容里的title|
|url|string|链接地址，消息内容里的url|
|thumbUrl|string|缩略图地址，消息内容里的thumburl|
|digest|string|摘要，消息内容里的digest|
|wxid|string|wxid|

### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
    "appName": "快手",
    "userName": "gh_271633",
    "title": "PC硬件、数码产品彻底反转",
    "url": "http://mp.weixin.qq.com/s?__biz=Mzg3MzYg==&mid=22440&idx=1&sn=bd8e8b0d9f2753f3c340&chksm=ced16f2ff9a6e639cc9bb76631ff03487f86486f0f29fcf9f8bed754354cb20eda31cc894a56&scene=0&xtrack=1#rd",
    "thumbUrl": "https://mmbiz.qpic.cn/sz__jpg/tpzwaqMCicQyEkpxmpmmP9KgoBHiciamYhqZ0ff4kNlozxgRq4AtEzibo4iaw/640?wxtype=jpeg&wxfrom=0",
    "digest": "这谁顶得住？",
    "wxid": "filehelper"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```

## 28.转发公众号消息**
### 接口功能
> 转发公众号消息

### 接口地址
> [/api/forwardPublicMsgByMsgId](/api/forwardPublicMsgByMsgId)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|msgId|number|msgId|
|wxid|string|wxid|

### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
   "msgId": 8871595889497690337,
    "wxid": "filehelper"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```

## 29.下载附件**
### 接口功能
> 下载附件，保存在微信文件目录下  wxid_xxx/wxhelper 目录下

### 接口地址
> [/api/downloadAttach](/api/downloadAttach)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|msgId|number|msgId|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
   "msgId": 887159588949767
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```


## 30.解码图片**
### 接口功能
> 解码图片

### 接口地址
> [/api/decodeImage](/api/decodeImage)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|filePath|string|待解码图片地址|
|storeDir|string|解码后图片的存储目录|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
   "filePath": "C:\\886206666148161980131.dat",
   "storeDir":"C:\\test"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```

## 31.获取语音**
### 接口功能
> 获取语音，SILK v3格式,可自行转换mp3格式

### 接口地址
> [/api/getVoiceByMsgId](/api/getVoiceByMsgId)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|msgId|number|消息id|
|storeDir|string|语音的存储目录|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
"msgId":78804324411226,
"storeDir":"c:\\test"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```

## 32.发送图片**
### 接口功能
> 发送图片

### 接口地址
> [/api/sendImagesMsg](/api/sendImagesMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid|string|wxid|
|imagePath|string|图片路径|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
    "wxid":"filehelper",
    "imagePath":"C:\\test.png"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```

## 33.发送自定义表情**
### 接口功能
> 发送自定义表情

### 接口地址
> [/api/sendCustomEmotion](/api/sendCustomEmotion)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid|string|wxid|
|filePath|string|表情路径，可以直接查询CustomEmotion表的MD5字段,路径规则见下面示例|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
    "wxid":"filehelper",
    "filePath":"C:\\wechatDir\\WeChat Files\\wxid_123\\FileStorage\\CustomEmotion\\8F\\8F6423BC2E69188DCAC797E279C81DE9"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```


## 34.发送小程序**
### 接口功能
> 发送小程序（待完善，不稳定）,相关参数可以参考示例的滴滴小程序的内容自行组装。

### 接口地址
> [/api/sendApplet](/api/sendApplet)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid|string|接收人wxid|
|waidConcat|string|app的wxid与回调信息之类绑定的拼接字符串，伪造的数据可以随意|
|appletWxid|string|app的wxid|
|jsonParam|string|相关参数|
|headImgUrl|string|头像url|
|mainImg|string|主图的本地路径,需要在小程序的临时目录下|
|indexPage|string|小程序的跳转页面|



### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
"wxid":"filehelper",
"waidConcat":"wxaf35009675aa0b2a_118",
"waid":"wxaf35009675aa0b2a",
"appletWxid":"gh_7a5c4141778f@app",
"jsonParam":"{\"current_path\":\"home/pages/index.html\",\"current_title\":\"\",\"image_url\":\"https://ut-static.udache.com/webx/mini-pics/U7mDFxU2yh-2-r1BJ-J0X.png\",\"scene\":1001,\"scene_note\":\"\",\"sessionId\":\"SessionId@1672284921_1#1692848476899\"}",
"headImgUrl":"http://mmbiz.qpic.cn/sz_mmbiz_png/9n47wQlh4dH8afD9dQ9uQicibRm5mYz3lawXCLMjmnzFicribH51qsFYxjzPEcTGHGmgX4lkAkQ3jznia8UDEtqsX1w/640?wx_fmt=png&wxfrom=200",
"mainImg":"C:\\wxid_123123\\Applet\\wxaf35009675aa0b2a\\temp\\2.png",
"indexPage":"pages/index/index.html"
}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```


## 35.拍一拍**
### 接口功能
> 拍一拍

### 接口地址
> [/api/sendPatMsg](/api/sendPatMsg)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|wxid|string|被拍人id|
|receiver|string|接收人id，可以是自己wxid，私聊好友wxid，群id|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,大于0成功, -1失败|
|msg|string|成功提示|
|data|object|null|

### 接口示例

入参：
``` javascript

{
"wxid":"wxid_1234",
"receiver":"wxid_1234",

}

```
响应：
``` javascript
{
    "code": 1,
    "data": {},
    "msg": "success"
}
```


## 36.OCR**
### 接口功能
> OCR识别文字，非0时再调用一次，一般需要调用2次

### 接口地址
> [/api/ocr](/api/ocr)

### HTTP请求方式
> POST  JSON

### 请求参数
|参数|必选|类型|说明|
|---|---|---|---|
|imagePath|string|图片全路径|


### 返回字段
|返回字段|字段类型|说明                              |
|---|---|---|
|code|int|返回状态,0成功, 非0时再调用一次|
|msg|string|成功提示|
|data|object|识别得结果|

### 接口示例

入参：
``` javascript

{

    "imagePath":"C:\\var\\123.jpg"
}
```
响应：
``` javascript
{
    "code": 0,
    "data": "17 硬卧下铺别人能不能坐?12306回应\r\n18 中南财大被解聘女讲师已失联4个多月\r\n19 新一轮存款利率下调即将落地\r\n",
    "msg": "success"
}
```
