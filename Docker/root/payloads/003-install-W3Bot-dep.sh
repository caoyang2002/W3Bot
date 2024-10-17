#!/usr/bin/env bash

# cd /home/app/W3Bot || exit
# pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# wine pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 切换到指定目录
# cd /home/app/W3Bot || exit

# # 使用官方 PyPI 库安装 Python 包
# echo "Installing Python packages from official PyPI repository..."
# pip3 install -r requirements.txt -i https://pypi.org/simple

# # 使用 wine 和官方 PyPI 库安装 Python 包
# echo "Installing Python packages using wine from official PyPI repository..."
# wine pip3 install -r requirements.txt -i https://pypi.org/simple

# echo "Package installation completed."


cd /home/app/W3Bot || exit

echo "Installing Python packages from official PyPI repository..."
python3.9 -m pip install --user -r requirements.txt -i https://pypi.org/simple

echo "Installing Python packages using wine from official PyPI repository..."
wine python3.9 -m pip install --user -r requirements.txt -i https://pypi.org/simple
wine python -m pip install pymem

echo "Package installation completed."
