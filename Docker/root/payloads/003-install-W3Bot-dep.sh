#!/usr/bin/env bash

cd /home/app/W3Bot || exit
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
wine pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
