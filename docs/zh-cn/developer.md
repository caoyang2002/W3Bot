# 参与开发 / 贡献

## 项目启动条件

**本项目使用 Python 3.9，请勿使用其他版本。**

- Python 3.9（项目的上游依赖为 3.9）
- wine-box:
  - Docker: https://hub.docker.com/r/henryxiaoyang/wine-box/
  - Github: https://github.com/HenryXiaoYang/wine-box/


## 贡献

- issue：清晰



## 使用远程强制覆盖本地

1. 获取远程最新内容

```bash
git fetch origin
```

2. 重置本地内容到远程状态

```bash
git reset --hard origin/main  # main 是你的分支名，可能是 master 或其他
```