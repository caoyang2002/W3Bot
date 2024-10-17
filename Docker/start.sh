#!/bin/bash

# 默认（不加参数）：在前台运行容器
# ./start.sh
# 在后台运行容器：
# ./start.sh --background
# 或
# ./start.sh -b
# 不运行容器：
# ./start.sh --no-run
# 或
# ./start.sh -n

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
sudo docker ps -a --format '{{.ID}}\t{{.Names}}' | grep -E 'docker-w3bot|W3Bot' | awk '{print $1}' | xargs -r docker rm -f
check_command_status

# 删除相关镜像
echo "删除相关镜像..."
sudo docker images --format '{{.ID}}\t{{.Repository}}' | grep -E 'docker-w3bot|W3Bot' | awk '{print $1}' | xargs -r docker rmi
check_command_status


# 删除相关卷
echo "删除相关卷..."
sudo docker volume ls -q --filter name=W3Bot | xargs -r docker volume rm
check_command_status

# 清理构建缓存
echo "清理 Docker 构建缓存..."
sudo docker builder prune -af
check_command_status

# 重新构建镜像，禁用缓存
echo "重新构建镜像，禁用缓存..."
sudo docker build --no-cache -t caoyang2002/w3bot:latest .
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
