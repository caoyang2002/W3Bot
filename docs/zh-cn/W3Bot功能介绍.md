# W3Bot 功能介绍

这一页介绍了所有官方 W3Bot 微信机器人用户可使用的功能、命令。

本介绍对应 `v0.0.7` 版本的W3Bot。

功能分为了 4 类：

- 实用功能⚙️
- 娱乐功能🔥
- 积分功能💰
- 管理员功能🔧

?> 所有功能都可用菜单查询。

## 链上功能

### 领取 Aptos Gas

<!-- chat:start -->

#### **Simons**

/gas 0x5dcb60faa729186d2bf13e21241e5edd0222c69ccb4973324511c21ee19a3626

#### **W3Bot**

✅ Gas 领取成功！
━━━━━━━━━━━━━━━
🌐 网络: TESTNET
📜 地址: 0x5dcb...9a3626
💧 实际到账: 1.00 APT
💰 当前余额: 45.99 APT
━━━━━━━━━━━━━━━
🔍 浏览器: https://explorer.aptoslabs.com/account/0x5dcb60faa729186d2bf13e21241e5edd0222c69ccb4973324511c21ee19a3626?network=testnet


#### **Simons**

/gas 0x5dcb60faa729186d2bf13e21241e5edd0222c69ccb4973324511c21ee19a3626

#### **W3Bot**

✅ Gas 领取成功！
━━━━━━━━━━━━━━━
🌐 网络: DEVNET
📜 地址: 0x5dcb...9a3626
💧 实际到账: 1.00 APT
💰 当前余额: 12.00 APT
━━━━━━━━━━━━━━━
🔍 浏览器: https://explorer.aptoslabs.com/account/0x5dcb60faa729186d2bf13e21241e5edd0222c69ccb4973324511c21ee19a3626?network=devnet

#### **Simons**

/gas

#### **W3Bot**

🌊 Aptos Gas 领取助手
━━━━━━━━━━━━━━━
📝 命令格式：

1️⃣ 默认领取 1 APT (testnet):
   /gas 0x<地址>

2️⃣ 指定数量:
   /gas <数量> 0x<地址>

3️⃣ 指定网络:
   /gas <网络> <数量> 0x<地址>

━━━━━━━━━━━━━━━
🌐 支持的网络:
• testnet (test)
• devnet (dev)

📌 示例:
/gas test 10 0x123...
/gas dev 5 0x123...
━━━━━━━━━━━━━━━

<!-- chat:end -->

### 创建地址

大部分管理员功能需要管理员权限，可以在位于项目根目录的主设置 `main_config.yml` 中设置管理员 `wxid`。

## 实用功能⚙️

### 1.0 菜单

一个微信机器人怎么能没有菜单？W3Bot 的菜单功能可以让你更方便地查看所有功能。

<!-- chat:start -->

#### **Simons**

菜单

#### **W3Bot**

实用功能⚙️
1.1 获取天气
1.2 获取新闻
1.3 ChatGPT
1.4 Hypixel玩家查询

娱乐功能🔥
2.1 随机图图
2.2 随机链接
2.3 五子棋

积分功能💰
3.1 签到
3.2 查询积分
3.3 积分榜
3.4 积分转送
3.5 积分抽奖
3.6 积分红包

🔧管理员功能
4.1 管理员菜单

帮助指令格式:
菜单 编号
例如:
菜单 1.1

#### **Simons**

菜单 1.2

#### **W3Bot**

1.2: 获取最新头条新闻📰
指令: 新闻

<!-- chat:end -->

### 1.1 获取天气

W3Bot 可以帮你查询全球任意城市的天气情况。

<!-- chat:start -->

#### **Simons**

天气 北京

#### **W3Bot**

北京 实时天气☁️
更新时间：2024-07-16T20:42+08:00⏰

🌡️当前温度：27℃
🌡️体感温度：30℃
☁️天气：多云
☀️紫外线指数：9
🌬️风向：西风
🌬️风力：1级
💦湿度：80%
🌧️降水量：0.0mm/h
👀能见度：10km

☁️未来3天 北京 天气：
7.17 晴 最高🌡️35℃ 最低🌡️22℃ ☀️紫外线:10
7.18 晴 最高🌡️35℃ 最低🌡️24℃ ☀️紫外线:10
7.19 多云 最高🌡️36℃ 最低🌡️24℃ ☀️紫外线:10

<!-- chat:end -->

### 1.2 获取新闻

W3Bot 可以帮你获取最新的头条新闻。

<!-- chat:start -->

#### **Simons**

获取新闻

#### **W3Bot**

📰 签订6艘、以人民币结算 我国船企再签大订单
🔗 https://news.china.com/domestic/945/20241019/47407481.html
🕒央视新闻客户端 2024-10-19

📰 签订6艘、以人民币结算 我国船企再签大订单
🔗 https://news.china.com/domestic/945/20241019/47407481.html
🕒 央视新闻客户端 2024-10-19

📰 签订6艘、以人民币结算 我国船企再签大订单
🔗 https://news.china.com/domestic/945/20241019/47407481.html
🕒 央视新闻客户端 2024-10-19
<!-- chat:end -->

### 1.3 ChatGPT

W3Bot可以调用ChatGPT，让你和机器人聊天。

?> 在设置中开启私聊ChatGPT后，可以在机器人私信直接问问题，不需要指令，还支持上下文关联！🎉

<!-- chat:start -->

#### **Simons**

gpt3 用简短的语言介绍一下Github

#### **W3Bot**

@Simons

已收到指令，处理中，请勿重复发送指令！👍

#### **W3Bot**

@Simons

因为你在白名单内，所以没扣除积分！👍

ChatGPT回答：

Github是一个基于云端的代码托管平台，它允许开发者存储、管理和共享代码。它提供了一个集中的位置，使团队成员可以协同开发项目，并追踪每个人的贡献。Github还提供了版本控制功能，允许开发者轻松地管理代码的变化和修复bug。此外，Github还是一个社交平台，开发者可以在上面发现其他人的项目，参与讨论和分享经验。总的来说，Github是一个强大的工具，为开发者提供了一个优秀的协作和学习平台。

⚙️ChatGPT版本：gpt-3.5-turbo

<!-- chat:end -->

<!-- chat:start -->

#### **Simons**

清除对话

#### **W3Bot(好友私聊)**

对话记录已清除！✅

#### **Simons**

后面用英文回答我

#### **W3Bot(好友私聊)**

Sure, please go ahead and ask your question in English.

#### **Simons**

1除以3等于几

#### **W3Bot(好友私聊)**

1 divided by 3 equals 0.3333 (repeating).
<!-- chat:end -->

### 1.4 Hypixel 玩家查询

W3Bot 可以帮你查询在我的世界服务器 Hypixel 中玩家的信息，数据等等。

<!-- chat:start -->

#### **Simons**

hypixel Technoblade

#### **W3Bot**

-----W3Bot-----
查询玩家 Technoblade 中，请稍候！🙂

#### **W3Bot**

-----W3Bot-----
🎮玩家：
[PIG+++] Technoblade [NERD]

--------

⚙️基础信息：
Multiplier: Level 296 (x8)
Level: 296.02
Karma: 151,277,505
Achievement Points: 11,450
Quests Completed: 3,057
Ranks Gifted: 0
First login:  2013-09-13 21:03 EDT

--------

🏹公会信息：
Name: technoclan
Members: 87
Rank: Guild Master
Joined: 2015/06/30 21:27:41

--------

ℹ️当前状态：
Status: Offline

#### **Simons**

hypixel bw Technoblade

#### **W3Bot**

-----W3Bot-----
查询玩家 Technoblade 中，请稍候！🙂

#### **W3Bot**

-----W3Bot-----
🎮玩家：
[PIG+++] Technoblade [NERD]

--------

🛏️起床战争信息：
⚔️模式：Solo
击杀：52
死亡：28
K/D：1.86
最终击杀：47
最终死亡：5
最终K/D：9.4
胜利：12
失败：9
W/L：1.33
破坏床数：51

⚔️模式：Doubles
击杀：3,519
死亡：2,318
K/D：1.52
最终击杀：5,451
最终死亡：204
最终K/D：26.72
胜利：813
失败：213
W/L：3.82
破坏床数：2,901
...省略...
<!-- chat:end -->

## 娱乐功能🔥

### 2.1 随机图图

W3Bot 可以帮你随机获取一张二次元图片。

!> Wiki 中图片都是固定的，不随机

<!-- chat:start -->

#### **Simons**

随机图图

#### **W3Bot**

![Random Picture](https://gitcode.net/qq_44112897/images/-/raw/master/comic/11.jpg)
<!-- chat:end -->

### 2.2 随机链接

W3Bot 可以帮你随机获取一个链接，可以说是更隐蔽的随机图图。

<!-- chat:start -->

#### **Simons**

随机链接

#### **W3Bot**

-----W3Bot-----
❓❓❓
❓: https://gitcode.net/qq_44112897/images/-/raw/master/comic/11.jpg
❓: https://gitcode.net/qq_44112897/images/-/raw/master/comic/12.jpg
❓: https://gitcode.net/qq_44112897/images/-/raw/master/comic/13.jpg
<!-- chat:end -->

### 2.3 五子棋

想要在群里和朋友玩五子棋？W3Bot 可以帮你创建并管理一场五子棋游戏。

!> 本功能仅可在群聊中使用

<!-- chat:start -->

#### **Simons**

五子棋 邀请 @Reggie

#### **W3Bot**

@Reggie
-----W3Bot-----
🎉您收到了一份来自 Simons 的五子棋比赛邀请！

⚙️请在60秒内发送下面的指令来接受邀请：
五子棋 接受 ABC123

#### **Reggie**

五子棋 接受 ABC123

#### **W3Bot**

@Reggie
-----W3Bot-----
🎉五子棋游戏 ABC123 开始！

⚫️黑方：Simons
⚪️白方：Reggie

⚫️黑方先手！

⏰每回合限时：60秒

⚙️请发送下面指令落子:
五子棋 下棋 横坐标纵坐标

⚙️例如: 五子棋 下棋 C5

#### **W3Bot**

![Gomoku Board 1](https://github.com/Simons/HXY_Readme_Images/blob/main/W3Bot/v0.0.7/wiki/function_introduction/gomoku_board_1.png?raw=true)

#### **Simons**

五子棋 下棋 i8

#### **W3Bot**

@Simons
-----W3Bot-----
⚫Simons 把棋子落在了 I8！
轮到 ⚪Reggie 下子了！
⏰限时：60秒

⚙️请发送下面指令落子:
五子棋 下棋 横坐标纵坐标

⚙️例如: 五子棋 下棋 C5

#### **W3Bot**

![Gomoku Board 2](https://github.com/Simons/HXY_Readme_Images/blob/main/W3Bot/v0.0.7/wiki/function_introduction/gomoku_board_2.png?raw=true)

#### **Reggie**

五子棋 下棋 I7

#### **W3Bot**

@Reggie
-----W3Bot-----
⚪Reggie 把棋子落在了 I7！
轮到 ⚫Simons 下子了！
⏰限时：60秒

⚙️请发送下面指令落子:
五子棋 下棋 横坐标纵坐标

⚙️例如: 五子棋 下棋 C5

#### **W3Bot**

![Gomoku Board 3](https://github.com/Simons/HXY_Readme_Images/blob/main/W3Bot/v0.0.7/wiki/function_introduction/gomoku_board_3.png?raw=true)

#### **Omitted**

此处省略一些聊天

#### **Simons**

五子棋 下棋 F9

#### **W3Bot**

@Simons
-----W3Bot-----
🎉五子棋游戏 ABC123 结束！🥳

⚫️黑方：Simons 获胜！🏆

#### **W3Bot**

![Gomoku Board 4](https://github.com/Simons/HXY_Readme_Images/blob/main/W3Bot/v0.0.7/wiki/function_introduction/gomoku_board_4.png?raw=true)
<!-- chat:end -->

## 积分功能💰

### 3.1 签到

在微信群中加入W3Bot后，群成员可以每天签到领取积分。积分可以用来使用ChatGPT、抽奖等、发积分红包等等。

!> 默认每天签到可以领取到随机 3-20 积分，范围可在签到设置中修改。

<!-- chat:start -->

#### **Simons**

签到

#### **W3Bot**

@Simons
-----W3Bot-----
签到成功！你领到了20个积分！✅

#### **Reggie**

签到

#### **W3Bot**

@Reggie
-----W3Bot-----
签到成功！你领到了3个积分！✅
<!-- chat:end -->

### 3.2 查询积分

有了积分系统，怎么能没有查询自己积分的功能呢？

<!-- chat:start -->

#### **Simons**

查询积分

#### **W3Bot**

@Simons
-----W3Bot-----
你有67点积分！👍
<!-- chat:end -->

### 3.3 积分榜

想要看看谁的积分最多？使用W3Bot可以查看积分榜。

<!-- chat:start -->

#### **Simons**

积分榜

#### **W3Bot**

-----W3Bot积分排行榜-----

1. xxxxxxx 7956分 👍
2. xxxx 5773分 👍
3. xxxxxx 4886分 👍
4. xxx 3840分 👍
5. xxxxx xxx 2899分 👍
6. xxxxx 2608分 👍
7. xxx 2595分 👍
8. xxxxxxxxxx 2291分 👍
9. xxxx 2043分 👍
10. xx 1992分 👍
11. xxxxx 1968分 👍
12. xxxxx 1913分 👍
13. xxxxx xx 1897分 👍
14. xxxxxxxxx 1896分 👍
15. xxxxxxxx 1889分 👍
16. xxx 1879分 👍
17. xxxxx 1767分 👍
18. xxx 1757分 👍
19. xxxx xxxxxxx xx xxxxxxx 1734分 👍
20. xxxxx 1679分 👍
21. xxxx 1650分 👍
22. x 1587分 👍
23. xxxx 1441分 👍
24. xxx 1430分 👍
25. xx 1352分 👍
26. xxxxx 1330分 👍
27. xxxxxxx 1327分 👍
28. xxxxxxx 1224分 👍
29. xx 1219分 👍
30. xxxxxxxx x 1202分 👍

<!-- chat:end -->

### 3.4 积分转送

一个积分体系怎么能没有交易系统？W3Bot的积分转送功能可以让你把你的积分转给其他人。

<!-- chat:start -->

#### **Simons**

转送积分 20 @Reggie

#### **W3Bot**

@Simons
-----W3Bot-----
转帐成功✅! 你现在有66点积分 Reggie现在有26点积分

#### **Reggie**

查询积分

#### **W3Bot**

@Reggie
-----W3Bot-----
你有26点积分！👍
<!-- chat:end -->

### 3.5 积分抽奖

W3Bot的积分抽奖功能可以让你用积分参与抽奖，赢取更多积分。

?> 抽奖的奖品和概率可以在抽奖设置中修改。

<!-- chat:start -->

#### **Simons**

抽奖 小

#### **W3Bot**

@Simons
----W3Bot抽奖----
🥳恭喜你在 1次 小抽奖 中抽到了：

🟩
绿
🟩

🎉总计赢取积分: 15🎉
🎉共计消耗积分：20🎉

概率请自行查询菜单⚙️

#### **Simons**

抽奖 中 5

#### **W3Bot**

@Simons
----W3Bot抽奖----
🥳恭喜你在 5次 中抽奖 中抽到了：

🟪🟩🟪🟩🟦
紫绿紫绿蓝
🟪🟩🟪🟩🟦

🎉总计赢取积分: 221🎉
🎉共计消耗积分：200🎉

概率请自行查询菜单⚙️
<!-- chat:end -->

### 3.6 积分红包

想发红包但没钱？W3Bot的积分红包功能可以让你用积分发红包给群里的其他人。

?> 红包的最高金额和最多数量可以在红包设置中修改。

<!-- chat:start -->

#### **Simons**

发红包 15 2

#### **W3Bot**

-----W3Bot-----
Simons 发送了一个红包！

🧧红包金额：15点积分
🧧红包数量：2个

🧧红包口令请见下图！

快输入指令来抢红包！抢红包 口令

#### **W3Bot**

![Red Packet Code](https://github.com/Simons/HXY_Readme_Images/blob/main/W3Bot/v0.0.7/wiki/function_introduction/red_packet_1.jpg?raw=true)

#### **Reggie**

抢红包 9bvx2

#### **W3Bot**

@Reggie
-----W3Bot-----
❌口令错误或无效！

#### **Reggie**

抢红包 qbvx2

#### **W3Bot**

@Reggie
-----W3Bot-----
🧧恭喜 Reggie 抢到了 4 点积分！
<!-- chat:end -->

## 管理员功能🔧

大部分管理员功能需要管理员权限，可以在位于项目根目录的主设置`main_config.yml`中设置管理员`wxid`。

!> `wxid`不是微信号！`wxid`是一个在微信内部使用的ID，用于识别用户。`wxid`一般以 `wxid_` 开头，例如 `wxid_0123456789abc`
，但是也有例外情况：一些老的微信账号的`wxid`不一定是以`wxid_`开头，可能是自定义的。

### 检查机器人状态

!> 本功能不是管理员也可以用

<!-- chat:start -->

#### **Simons**

机器人状态

#### **W3Bot**

-----W3Bot-----
Bot Running😊
Bot version: v0.0.6
Github: https://github.com/caoyang2002/W3Bot

#### **Reggie**

机器人状态

#### **W3Bot**

Bot Running😊
Bot version: v0.0.6
Github: https://github.com/caoyang2002/W3Bot
<!-- chat:end -->

### 获取机器人通讯录

!> 本功能仅管理员可用

可以用这个功能查询到机器人的通讯录。

<!-- chat:start -->

#### **Simons**

获取机器人通讯录

#### **W3Bot**

(一个Excel表格)

<!-- chat:end -->

### 管理积分

!> 本功能仅管理员可用

管理员可以通过这个修改用户的积分，可以用wxid也可以@。

<!-- chat:start -->

#### **Simons**

管理积分 wxid_0123456789abcde 加 10

#### **W3Bot**

-----W3Bot-----
😊成功给wxid_0123456789abcde加了10点积分！他现在有15点积分！

#### **Simons**

管理积分 @Reggie 减 10

#### **W3Bot**

-----W3Bot-----
😊成功给wxid_0123456789abcde减了10点积分！他现在有5点积分！

#### **Simons**

管理积分 wxid_0123456789abcde 10

#### **W3Bot**

-----W3Bot-----
😊成功将wxid_0123456789abcde的积分设置为10！
<!-- chat:end -->

### 管理白名单

!> 本功能仅管理员可用

管理员可以通过这个功能管理白名单，有白名单者使用ChatGPT功能不扣积分。可以用`wxid`也可以用@。

<!-- chat:start -->

#### **Simons**

管理白名单 wxid_0123456789abcde 加入

#### **W3Bot**

-----W3Bot-----
成功修改wxid_0123456789abcde的白名单！😊

#### **Simons**

管理白名单 @Reggie 删除

#### **W3Bot**

-----W3Bot-----
成功修改wxid_0123456789abcde的白名单！😊
<!-- chat:end -->

### 查看已加载插件列表

!> 本功能仅管理员可用

管理员可以通过这个功能查看已加载的插件列表。

<!-- chat:start -->

#### **Simons**

管理插件 列表

#### **W3Bot**

-----W3Bot-----
已加载插件列表：
admin_signin_reset
points_trade
manage_plugins
bot_status
hypixel_info
red_packet
weather
sign_in
query_points
gpt4
get_contact_list
admin_points
random_picture
lucky_draw
random_picture_link
admin_whitelist
points_leaderboard
gpt
menu
news
gomoku
<!-- chat:end -->

### 热加载/卸载/重载插件

!> 本功能仅管理员可用

管理员可以通过这个功能在不重启机器人的情况下加载，重载，卸载插件。

<!-- chat:start -->

#### **Simons**

管理插件 卸载 lucky_draw

#### **W3Bot**

-----W3Bot-----
卸载插件lucky_draw成功！✅

#### **Simons**

管理插件 加载 lucky_draw

#### **W3Bot**

-----W3Bot-----
加载插件lucky_draw成功！✅

#### **Simons**

管理插件 重载 lucky_draw

#### **W3Bot**

-----W3Bot-----
重载插件lucky_draw成功！✅
<!-- chat:end -->

### 重置签到冷却

!> 本功能仅管理员可用

机器人出错而崩溃了，导致群友没签到而闹事？管理员可以通过这个功能重置签到冷却时间。

<!-- chat:start -->

#### **Simons**

重置签到冷却

#### **W3Bot**

-----W3Bot-----
😊成功重置签到状态！
<!-- chat:end -->
