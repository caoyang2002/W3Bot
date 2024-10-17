FROM henryxiaoyang/wechat-box-3.9.5.81:latest

# 安装必要的依赖
RUN apt-get update && apt-get install -y software-properties-common

# 添加 deadsnakes PPA 仓库，这个仓库包含了多个 Python 版本
RUN add-apt-repository ppa:deadsnakes/ppa

# 更新包列表
RUN apt-get update

# 安装 Python 3.9
RUN apt-get install -y python3.9 python3.9-venv python3.9-dev

# 安装 pip for Python 3.9
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.9 get-pip.py && \
    rm get-pip.py

# 设置 Python 3.9 为默认 Python 版本
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# 验证 Python 版本
RUN python3 --version

# 清理 apt 缓存以减小镜像大小
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PYTHONPATH="/home/app/.local/lib/python3.9/site-packages:${PYTHONPATH}"

# 原有的 Dockerfile 内容
RUN sudo rm -rf /payloads

COPY root/ /

# init with GUI
RUN bash -c 'nohup /entrypoint.sh 2>&1 &' && sleep 5 && /payloads.sh \
    && sudo cp -r /wechat-etc/* /etc/ \
    && sudo rm /tmp/.X0-lock

# 安装依赖
COPY requirements.txt /home/app/W3Bot/
RUN python3.9 -m pip install --user -r /home/app/W3Bot/requirements.txt

# settings
ENTRYPOINT ["/wx-entrypoint.sh"]
