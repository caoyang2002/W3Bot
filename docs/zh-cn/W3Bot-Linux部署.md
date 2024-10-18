# W3Bot Linux 部署

这一页写了在 Linux 上部署 W3Bot 的方法。

本篇部署教程适用于 `W3Bot v0.0.7`。

## 前言

在Linux上部署 `W3Bot` 需要用到 `Docker`，`Docker` 容器中运用了 `wine`，它对环境要求**极高**。

[已知可以部署的发行版：](https://github.com/ChisBread/wechat-service/issues/1#issuecomment-1252083579)

- `Ubuntu`
- `Arch`
- `Debian`
- `DSM6.2.3`
- `DSM7.0`

不可部署的发行版：

- `CentOS`

欢迎各位开 `issue` 或者 `pull request` 来反馈！

[CentOS部署失败](https://github.com/ChisBread/wechat-service/issues/1)

由于运行 PC 版微信将消耗很多资源，请确认服务器配置。

服务器配置要求：

- 2核2G以上

## 部署

### 1. 安装 Docker

装好了可跳过

官方教程链接🔗：

https://docs.docker.com/get-docker/

### 2. 安装 Docker Compose

一样，已装好可跳过

https://docs.docker.com/compose/install/

### 3. 拉取 Docker 镜像

这一步以及后面遇到权限问题请在前面加个 `sudo`。

```bash
docker pull caoyang2002/W3Bot:latest
```

### 4. 启动容器

指令：

```bash
docker run -d \
  --name W3Bot \
  --restart unless-stopped \
  -e WC_AUTO_RESTART=yes \
  -p 4000:8080 \
  --add-host dldir1.qq.com:127.0.0.1 \
  -v W3Bot:/home/app/W3Bot/ \
  -v W3Bot-wechatfiles:/home/app/WeChat\ Files/ \
  -t caoyang2002/W3Bot:latest
```

Docker-compose:

`W3Bot/Docker/docker-compose.yaml`

```yaml
version: "3.3"

services:
    W3Bot:
        image: "caoyang2002/W3Bot:latest"
        restart: unless-stopped
        container_name: "W3Bot"
        environment:
            WC_AUTO_RESTART: "yes"
        ports:
            - "4000:8080"
        extra_hosts:
            - "dldir1.qq.com:127.0.0.1"
        volumes:
              - "W3Bot:/home/app/W3Bot/"
              - "W3Bot-wechatfiles:/home/app/WeChat Files/"
        tty: true

volumes:
    W3Bot:
    W3Bot-wechatfiles:
```

### 5. 登陆微信

在浏览器中打开 `http://<你的ip地址>:4000/vnc.html` 访问 VNC。

![VNC WeChat Login](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/W3Bot/v0.0.7/wiki/windows_deployment/vnc_wechat_login.png?raw=true)

扫描微信二维码并登录，登陆后 W3Bot 将自动启动。

!>如果遇到微信崩溃，可尝试重启容器重新按步骤登陆。

### 6. 配置 W3Bot 设置

如果使用的步骤4的启动指令，W3Bot的文件已被持久化到 `/var/lib/docker/volumes/W3Bot`，也就是 `W3Bot` 卷。

```bash
cd /var/lib/docker/volumes/W3Bot/_data
```

在这个目录下可以看到 `main_config.yml`，修改这个文件即可。

### 7. 重启容器

```bash
docker restart wechat-service-W3Bot
```

修改主设置后需要重启容器。重启后需要访问VNC重新扫码并登陆微信！

### 8. 测试是否部署成功

在微信中向W3Bot私聊`菜单`，如果返回菜单则部署成功。

<!-- chat:start -->

#### **Simons**

菜单

#### **W3Bot**

-----W3Bot菜单------

实用功能⚙️

1.1 获取天气

1.2 获取新闻

1.3 ChatGPT

1.4 Hypixel玩家查询



娱乐功能🔥

2.1 随机图图

2.2 随机链接

2.3 随机群成员

2.4 五子棋



积分功能💰

3.1 签到

3.2 查询积分

3.3 积分榜

3.4 积分转送

3.5 积分抽奖

3.6 积分红包



🔧管理员功能

4.1 管理员菜单



获取菜单指令格式: 菜单 编号

例如：菜单 1.1
<!-- chat:end -->

可以开始用W3Bot了！

如果失败，可以看看容器日志并发`issue`询问。

```bash
docker logs W3Bot -f --tail 100
```

### 9. 设置VNC密码

VNC默认是没有密码的，强烈推荐设置密码。

#### 1. 进入容器bash

```bash
docker exec -it W3Bot /bin/bash
```

#### 2. 设置密码

请设置一个强密码避免暴力破解

```bash
# 跟提示设置密码
x11vnc --storepasswd
```

#### 3. 编辑文件

将第二行改成：

```command=x11vnc -forever -shared -rfbauth /home/app/.vnc/passwd```

```bash
# 修改这个文件
vi /etc/supervisord.d/x11vnc.conf
```

现在第二行应该是：

```command=x11vnc -forever -shared -rfbauth /home/app/.vnc/passwd```

#### 4. 退出容器bash

```bash
exit
```

#### 5. 重启容器

```bash
docker restart W3Bot
```

现在用网页连接vnc会请求密码

#### 6. 登陆VNC后重新扫描二维码登陆微信

登陆后，W3Bot会自动启动
