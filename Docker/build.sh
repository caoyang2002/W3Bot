#!/bin/bash

# 检查是否有 docker-w3bot 容器
if [ "$(docker ps -aq -f name=docker-w3bot)" ]; then
  echo "Removing existing docker-w3bot container..."
  docker rm -f docker-w3bot
fi

# 检查是否有 W3Bot 容器
if [ "$(docker ps -aq -f name=W3Bot)" ]; then
  echo "Removing existing W3Bot container..."
  docker rm -f W3Bot
fi

# 检查是否有 docker-w3bot 镜像
if [ "$(docker images -q docker-w3bot:latest)" ]; then
  echo "Removing existing docker-w3bot image..."
  docker rmi docker-w3bot:latest
fi

# 检查是否有 W3Bot 镜像
if [ "$(docker images -q W3Bot:latest)" ]; then
  echo "Removing existing W3Bot image..."
  docker rmi W3Bot:latest
fi

# 构建新的镜像
echo "构建 caoyang2002/w3bot:latest 镜像..."
sudo docker build -t caoyang2002/w3bot:latest .

echo "已构建镜像: "
sudo docker images

echo "启动镜像"
sudo docker-compose up

echo "执行完毕"
