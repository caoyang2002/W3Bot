#!/usr/bin/env bash

# cd /home/app/W3Bot || exit
# pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# wine pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 切换到指定目录
cd /home/app/W3Bot || exit

# 使用官方 PyPI 库安装 Python 包
echo "Installing Python packages from official PyPI repository..."
pip3 install -r requirements.txt

# 使用 wine 和官方 PyPI 库安装 Python 包
echo "Installing Python packages using wine from official PyPI repository..."
wine pip3 install -r requirements.txt

echo "Package installation completed."
