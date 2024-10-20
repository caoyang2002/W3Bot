# W3Bot 微信机器人

> 本机器人 frok 自 [XYBot](https://github.com/HenryXiaoYang/XYBot)

<p align="center">
    <img alt="XYBot微信机器人logo" width="240" src="./docs/images/w3bot.png">
</p>


# 面对 Web3 治理的优化

## 机器人清理

1. 使用行为特征分析，检测机器人，超出阈值者第一次警告，第二次列入监控名单，第三次列入黑名单

2. 本机器人会保留非白名单用户行为特征

3. 知识库问答


# 自动运行

```bash
pip install -r requirements.txt
python start.py

# of

run.sh
```


# docker 自部署

```bash
# 构建 Docker 镜像
sudo docker build -t caoyang2002/w3bot:latest .

# 运行 Docker 容器
docker-compose up

# 交互
docker exec -it w3bot /bin/bash

# 停止 Docker 容器
docker-compose down

# 删除 Docker 镜像
docker rmi -f caoyang2002/w3bot:latest
```





# 开发

## Linux 一键部署

### 安装 Docker

装好了可跳过

官方教程链接🔗：

https://docs.docker.com/get-docker/

### 2. 安装 Docker Compose

一样，已装好可跳过

https://docs.docker.com/compose/install/

### 3. 拉取 Docker 镜像

这一步以及后面遇到权限问题请在前面加个 `sudo`。

```bash
docker pull henryxiaoyang/w3bot:latestCopy to clipboardErrorCopied
```

### 4. 启动容器

指令：

```bash
docker run -d \
  --name XYBot \
  --restart unless-stopped \
  -e WC_AUTO_RESTART=yes \
  -p 4000:8080 \
  --add-host dldir1.qq.com:127.0.0.1 \
  -v XYBot:/home/app/XYBot/ \
  -v XYBot-wechatfiles:/home/app/WeChat\ Files/ \
  -t henryxiaoyang/w3bot:latestCopy to clipboardErrorCopied
```

Docker-compose:

```
XYBot/Docker/docker-compose.yaml
version: "3.3"

services:
    w3bot:
        image: "henryxiaoyang/w3bot:latest"
        restart: unless-stopped
        container_name: "XYBot"
        environment:
            WC_AUTO_RESTART: "yes"
        ports:
            - "4000:8080"
        extra_hosts:
            - "dldir1.qq.com:127.0.0.1"
        volumes:
              - "XYBot:/home/app/XYBot/"
              - "XYBot-wechatfiles:/home/app/WeChat Files/"
        tty: true

volumes:
    XYBot:
    XYBot-wechatfiles:Copy to clipboardErrorCopied
```

### 5. 登陆微信

在浏览器中打开 `http://<你的ip地址>:4000/vnc.html` 访问 VNC。

![VNC WeChat Login](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/wiki/windows_deployment/vnc_wechat_login.png?raw=true)

扫描微信二维码并登录，登陆后 XYBot 将自动启动。

---

# 原文档介绍

XYBot 是一个可运行于 Linux 和 Windows 的基于 Hook 的微信机器人。😊 具有高度可自定义性，支持自我编写插件。🚀

XYBot 提供了多种功能，包括获取天气 🌤️、获取新闻 📰、ChatGPT 聊天 🗣️、Hypixel 玩家查询 🎮、随机图片 📷、随机链接 🔗、随机群成员 👥、五子棋 ♟️、签到 ✅、查询积分 📊、积分榜 🏆、积分转送 💰、积分抽奖 🎁、积分红包 🧧 等。🎉

XYBot 拥有独立的经济系统，其中基础货币称为”积分“。💰

XYBot 还提供了管理员功能，包括修改积分 💰、修改白名单 📝、重置签到状态 🔄、获取机器人通讯录 📚、热加载/卸载/重载插件 🔄 等。🔒

XYBot 详细的部署教程可以在项目的 Wiki 中找到。📚 同时，XYBot 还支持自我编写插件，用户可以根据自己的需求和创造力编写自定义插件，进一步扩展机器人的功能。💡

✅ 高度可自定义！
✅ 支持自我编写插件！

<p align="center">
    <a href="https://opensource.org/licenses/"><img src="https://img.shields.io/badge/License-GPL%20v3-red.svg" alt="GPLv3 License"></a>
    <a href="https://github.com/HenryXiaoYang/XYBot"><img src="https://img.shields.io/badge/Version-0.0.7-orange.svg" alt="Version"></a>
    <a href="https://yangres.com"><img src="https://img.shields.io/badge/Blog-@HenryXiaoYang-yellow.svg" alt="Blog"></a>
</p>

## 公告

由于需要频繁的更新维护，XYBot 版本号格式将会发生变化，v0.0.7 后面的版本号将会按照以下格式进行更新：

v 大版本.功能版本.Bug 修复版本

例如：

- v1.0.1 是 v1.0.0 的 Bug 修复版本
- v1.1.0 是 v1.0.0 的功能版本
- v1.1.1 是 v1.1.0 的 Bug 修复版本

## 功能列表

用户功能:

- 获取天气 🌤️
- 获取新闻 📰
- ChatGPT🗣️
- Hypixel 玩家查询 🎮
- 随机图图 📷
- 随机链接 🔗
- 五子棋 ♟️
- 签到 ✅
- 查询积分 📊
- 积分榜 🏆
- 积分转送 💰
- 积分抽奖 🎁
- 积分红包 🧧

管理员功能:

- 修改积分 💰
- 修改白名单 📝
- 重置签到状态 🔄
- 获取机器人通讯录 📚
- 热加载/卸载/重载插件 🔄
- 查看已加载插件 ℹ️

## XYBot 文档 📄

文档中有完整的功能介绍，部署教程，配置教程，插件编写教程。

**[🔗XYBot 文档](https://henryxiaoyang.github.io/XYBot)**

## 功能演示

菜单
![Menu Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/menu.png?raw=true)

随机图片
![Random Picture Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/random_picture.png?raw=true)

ChatGPT
![ChatGPT Example 1](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/gpt3.png?raw=true)
![ChatGPT Example 2](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/gpt4.png?raw=true)

私聊 ChatGPT
![Private ChatGPT Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/private_gpt.png?raw=true)

天气查询
![Weather Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/weather.png?raw=true)

五子棋
![Gomoku Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/gomoku.png?raw=true)

## 自我编写插件 🧑‍💻

请参考模板插件：

**[🔗 模板插件仓库️](https://github.com/HenryXiaoYang/XYBot-Plugin-Framework)**

## XYBot 交流群

<p align="center">
    <img alt="XYBot二维码" width="360" src="https://file.yangres.com/w3bot-wechatgroup.jpeg">
</p>

[**🔗 图片会被缓存，点我查看最新二维码**](https://file.yangres.com/w3bot-wechatgroup.jpeg)

## 捐赠

<p align="center">
    <img alt="爱发电二维码" width="360" src="https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/aifadian.jpg?raw=true">
    <p align="center">你的赞助是我创作的动力！🙏</p>
</p>

## FAQ❓❓❓

#### ARM 架构能不能运行?🤔️

不行

#### 用的什么微信版本?🤔️

3.9.5.81😄

#### 最长能运行多久？🤔️

XYBot 内置了防微信自动退出登录功能，可以保持长时间运行。

## 特别感谢

https://github.com/ChisBread/wechat-box/ 感谢提供了 Docker 容器相关的信息！

https://github.com/sayue2019/wechat-service-allin 感谢提供了 Docker 容器相关的信息！

https://github.com/cixingguangming55555/wechat-bot v0.0.7 之前用的 Hook，非常好用，感谢！

https://github.com/ttttupup/wxhelper/ v0.0.7 及之后用的 Hook，功能很多，感谢！

https://github.com/miloira/wxhook 感谢这个项目提供了 Windows 环境下微信的启动与注入 Hook 的工具！

https://github.com/nefarius/Injector 感谢这个项目提供了 Docker 环境下微信的注入 Hook 的工具！

https://github.com/lich0821 感谢这个项目的作者写的微信版本号修复代码！参考了下，非常感谢！

## ⭐️Star History⭐️

<p align="center">
    <picture>
      <source
        media="(prefers-color-scheme: dark)"
        srcset="
          https://api.star-history.com/svg?repos=HenryXiaoYang/XYBot&type=Date&theme=dark
        "
      />
      <source
        media="(prefers-color-scheme: light)"
        srcset="
          https://api.star-history.com/svg?repos=HenryXiaoYang/XYBot&type=Date
        "
      />
      <img
        alt="XYBot Star History"
        width="600"
        src="https://api.star-history.com/svg?repos=HenryXiaoYang/XYBot&type=Date"
      />
    </picture>
</p>
