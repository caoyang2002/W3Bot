FROM henryxiaoyang/wechat-box-3.9.5.81:latest

RUN sudo rm /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-*.list || true

# 更新包列表
RUN sudo apt-get update

# 安装必要的依赖
RUN sudo apt-get install -y \
    software-properties-common \
    wget \
    gnupg

# 添加 Debian 的 backports 仓库（如果还没有的话）
RUN echo "deb http://deb.debian.org/debian bullseye-backports main" | sudo tee -a /etc/apt/sources.list

# 更新包列表
RUN sudo apt-get update

# 从 backports 安装 Python 3.9
RUN sudo apt-get install -y -t bullseye-backports python3.9 python3.9-venv python3.9-dev

# 安装 pip for Python 3.9
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    sudo python3.9 get-pip.py && \
    rm get-pip.py

# 设置 Python 3.9 为默认 Python 版本
RUN sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# 验证 Python 版本
RUN python3 --version

# 清理 apt 缓存以减小镜像大小
RUN sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*

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
