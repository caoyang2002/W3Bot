#!/bin/bash

echo "检查是否存在 W3Bot 容器"
sudo docker ps -a

echo "检查是否存在 W3Bot 镜像"
sudo docker images

# 检查是否有 docker-w3bot 容器
if [ "$(sudo docker ps -aq -f name=docker-w3bot)" ]; then
  echo "Removing existing docker-w3bot container..."
  docker rm -f docker-w3bot
fi

# 检查是否有 W3Bot 容器
if [ "$(sudo docker ps -aq -f name=W3Bot)" ]; then
  echo "Removing existing W3Bot container..."
  sudo docker rm -f W3Bot
fi

# 检查是否有 docker-w3bot 镜像
if [ "$(sudo docker images -q docker-w3bot:latest)" ]; then
  echo "Removing existing docker-w3bot image..."
  sudo docker rmi docker-w3bot:latest
fi

# 检查是否有 W3Bot 镜像
if [ "$(sudo docker images -q W3Bot:latest)" ]; then
  echo "Removing existing W3Bot image..."
  sudo docker rmi W3Bot:latest
fi

echo "再次检查是否存在 W3Bot 容器"
sudo docker ps -a

echo "再次检查是否存在 W3Bot 镜像"
sudo docker images

# 构建新的镜像
echo "构建 caoyang2002/w3bot:latest 镜像..."
sudo docker build -t caoyang2002/w3bot:latest .

echo "已构建镜像: "
sudo docker images

echo "启动镜像"
sudo docker-compose up

echo "执行完毕"
