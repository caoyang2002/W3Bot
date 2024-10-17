#!/bin/bash

set -e  # 启用错误检查，如果任何命令失败脚本将立即退出

function check_command_status {
    if [ $? -ne 0 ]; then
        echo "错误: 上一个命令执行失败，脚本终止。"
        exit 1
    fi
}


parse_args() {
    CONTAINER_MODE="foreground"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --background|-b)
                CONTAINER_MODE="background"
                shift
                ;;
            --no-run|-n)
                CONTAINER_MODE="no-run"
                shift
                ;;
            *)
                echo "未知选项: $1"
                exit 1
                ;;
        esac
    done
}

# 在脚本开始时调用这个函数
parse_args "$@"

echo "检查当前 Docker 容器状态"
sudo docker ps -a
check_command_status

echo "检查当前 Docker 镜像状态"
sudo docker images
check_command_status

# 删除相关容器
echo "删除相关容器..."
docker ps -a --format '{{.ID}}\t{{.Names}}' | grep -E 'docker-w3bot|W3Bot' | awk '{print $1}' | xargs -r docker rm -f
check_command_status

# 删除相关镜像
echo "删除相关镜像..."
docker images --format '{{.ID}}\t{{.Repository}}' | grep -E 'docker-w3bot|W3Bot' | awk '{print $1}' | xargs -r docker rmi
check_command_status

echo "再次检查 Docker 容器状态"
sudo docker ps -a
check_command_status

echo "再次检查 Docker 镜像状态"
sudo docker images
check_command_status

# 构建新的镜像
echo "构建 caoyang2002/w3bot:latest 镜像..."
sudo docker build -t caoyang2002/w3bot:latest .
check_command_status

echo "已构建镜像: "
sudo docker images
check_command_status

echo "启动镜像"
case $CONTAINER_MODE in
    background)
        echo "在后台启动容器..."
        sudo docker-compose up -d
        ;;
    foreground)
        echo "在前台启动容器..."
        sudo docker-compose up
        ;;
    no-run)
        echo "不启动容器。"
        ;;
esac
check_command_status

echo "执行完毕"
