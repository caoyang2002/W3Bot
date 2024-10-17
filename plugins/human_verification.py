import sqlite3
from collections import Counter
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
import pywxdll
import yaml
from loguru import logger
from utils.plugin_interface import PluginInterface
from utils.chatroom_database import ChatroomDatabase
import os

class human_verification(PluginInterface):
    def __init__(self):
        config_path = 'plugins/human_verification.yml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f.read())
        self.plugin_setting = config['plugin_setting']

        main_config_path = 'main_config.yml'
        with open(main_config_path, 'r', encoding='utf-8') as f:
            main_config = yaml.safe_load(f.read())

        self.bot_version = main_config["bot_version"]
        self.ip = main_config["ip"]
        self.port = main_config["port"]
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.out_message = ""

        # 初始化数据库连接
        self.db = ChatroomDatabase()

        # 加载自定义字体文件
        # custom_font = FontProperties(fname='../assets/SourceHanSansHWSC-Regular.otf')
        # 设置matplotlib配置，使用自定义字体
        plt.rcParams['font.sans-serif'] =  ['WenQuanYi Micro Hei']
        plt.rcParams['axes.unicode_minus'] = False

    def analyze_user(self, user_wxid,group_wxid,recv):
        """
        分析指定用户的行为，判断是人类还是AI
        :param user_wxid: 用户的微信ID
        :param recv: 接收到的消息
        :return: 分析结果文本
        """
        # 获取用户数据
        user_data = self.db.get_user_data(group_wxid,user_wxid)

        if not user_data:
            return "数据库中未找到该用户。"

        user_id = user_data[0]

        # 获取用户消息
        messages = self.db.get_messages_by_user_wxid(user_id)

        # 执行分析
        analysis_result = self._analyze_messages(messages,recv)

        # 生成并保存可视化图表
        self._generate_visualization(analysis_result, user_wxid)

        return analysis_result

    def _analyze_messages(self, messages,recv):
        user_name = recv['displayFullContent'].split(':')[0]
        """
        分析用户消息
        :param messages: 用户的消息列表
        :return: 分析结果文本
        """
        if not messages:
            return f"未找到该用户的消息。: {user_name}"

        total_messages = len(messages)
        message_contents = [msg[4] for msg in messages]  # msg[4] 是 MESSAGE_CONTENT
        message_types = [msg[6] for msg in messages]  # msg[6] 是 MESSAGE_TYPE

        # 基本指标计算
        avg_message_length = sum(len(content) for content in message_contents) / total_messages
        time_diffs = self._calculate_time_diffs(messages)
        avg_time_between_messages = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        word_frequency = Counter(" ".join(message_contents).split())
        unique_words = len(word_frequency)
        repetitive_patterns = self._check_repetitive_patterns(message_contents)
        emoji_ratio = self._calculate_emoji_ratio(message_contents)

        # 新增分析
        type_diversity = len(set(message_types)) / len(message_types)
        vocabulary_richness = self._calculate_vocabulary_richness(message_contents)
        sentiment_variance = self._calculate_sentiment_variance(message_contents)
        topic_coherence = self._calculate_topic_coherence(message_contents)

        # 决策逻辑
        features = [
            avg_message_length / 100,  # 归一化
            min(avg_time_between_messages / 3600, 1),  # 限制在0-1之间
            unique_words / total_messages,
            int(repetitive_patterns),
            emoji_ratio,
            type_diversity,
            vocabulary_richness,
            sentiment_variance,
            topic_coherence
        ]

        # 使用加权求和方法
        weights = [0.1, 0.15, 0.1, 0.1, 0.05, 0.1, 0.15, 0.1, 0.15]
        weighted_sum = sum(f * w for f, w in zip(features, weights))

        # 使用 sigmoid 函数将结果映射到0-1之间
        normalized_score = 1 / (1 + np.exp(-weighted_sum))

        classification = "AI" if normalized_score > 0.5 else "人类"
        confidence = abs(normalized_score - 0.5) * 2  # 将0.5-1的范围映射到0-1

        analysis = f"""
分析结果：
目标: {user_name}
总消息数: {total_messages}
平均消息长度: {avg_message_length:.2f} 字符
消息间平均时间: {avg_time_between_messages:.2f} 秒
唯一词汇比例: {unique_words / total_messages:.2f}
检测到重复模式: {"是" if repetitive_patterns else "否"}
表情使用比例: {emoji_ratio:.2f}
消息类型多样性: {type_diversity:.2f}
词汇丰富度: {vocabulary_richness:.2f}
情感变化程度: {sentiment_variance:.2f}
话题连贯性: {topic_coherence:.2f}

分类: {classification} (置信度: {confidence:.2f})
"""

        return analysis

    def _calculate_time_diffs(self, messages):
        """计算消息间的时间差"""
        time_diffs = []
        for i in range(1, len(messages)):
            time1 = datetime.strptime(messages[i-1][5], "%Y-%m-%d %H:%M:%S")
            time2 = datetime.strptime(messages[i][5], "%Y-%m-%d %H:%M:%S")
            time_diffs.append((time2 - time1).total_seconds())
        return time_diffs

    def _check_repetitive_patterns(self, messages, threshold=3):
        """检查消息中的重复模式"""
        joined_messages = " ".join(messages)
        words = joined_messages.split()
        for i in range(len(words)):
            for j in range(i+1, len(words)):
                pattern = " ".join(words[i:j])
                if len(pattern.split()) >= threshold and joined_messages.count(pattern) > 1:
                    return True
        return False

    def _calculate_emoji_ratio(self, messages):
        """计算表情使用比例"""
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        emoji_count = sum(len(emoji_pattern.findall(msg)) for msg in messages)
        return emoji_count / len(messages)

    def _calculate_vocabulary_richness(self, messages):
        """计算词汇丰富度（使用Type-Token Ratio）"""
        words = " ".join(messages).split()
        return len(set(words)) / len(words)

    def _calculate_sentiment_variance(self, messages):
        """计算情感变化程度（这里使用一个简化的方法，实际应用中可以使用更复杂的情感分析库）"""
        positive_words = set(['好', '喜欢', '开心', '棒', '优秀'])
        negative_words = set(['坏', '讨厌', '难过', '糟糕', '失败'])
        sentiments = []
        for msg in messages:
            words = set(msg.split())
            positive_score = len(words.intersection(positive_words))
            negative_score = len(words.intersection(negative_words))
            sentiments.append(positive_score - negative_score)
        return np.var(sentiments)

    def _calculate_topic_coherence(self, messages, n_clusters=5):
        """计算话题连贯性（使用TF-IDF和K-means聚类）"""
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(messages)
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(tfidf_matrix)
        distances = kmeans.transform(tfidf_matrix)
        coherence = np.mean(np.min(distances, axis=1))
        return 1 / (1 + coherence)  # 转换为0-1之间的值，越大表示越连贯

    def _generate_visualization(self, analysis_result, user_wxid):
        """
        生成分析结果的可视化图表
        :param analysis_result: 分析结果文本
        :param user_wxid: 用户的微信ID
        """
        # 从分析结果中提取数据
        lines = analysis_result.strip().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                try:
                    data[key.strip()] = float(value.split()[0])
                except ValueError:
                    pass

        # 创建雷达图
        categories = list(data.keys())[:-2]  # 排除 "分类" 和 "置信度"
        values = [data[cat] for cat in categories]

        # 归一化值到0-1之间
        min_val, max_val = min(values), max(values)
        normalized_values = [(v - min_val) / (max_val - min_val) for v in values]

        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        normalized_values = np.concatenate((normalized_values, [normalized_values[0]]))  # 闭合多边形
        angles = np.concatenate((angles, [angles[0]]))  # 闭合多边形

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.plot(angles, normalized_values)
        ax.fill(angles, normalized_values, alpha=0.25)
        ax.set_thetagrids(angles[:-1] * 180/np.pi, categories)
        ax.set_title(f"用户 {user_wxid} 的行为特征雷达图")
        plt.tight_layout()
        plt.savefig(f"{user_wxid}_human_verification.png")
        plt.close()

    async def run(self, recv):
        group_wxid = recv['from'] # gropu wxid
        user_wxid = ''
        if recv['fromType'] == 'friend':
            user_wxid = recv['sender'] # wxid
        elif recv['fromType'] == 'chatroom':
            user_wxid = recv['sender'] # wxid
            logger.info("[收到用户消息] ",user_wxid)
        out_message = self.analyze_user(user_wxid,group_wxid,recv)

        logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
        self.bot.send_at_msg(recv["from"], out_message, [user_wxid])
        # self.bot.send_text_msg(recv["from"], out_message)  # 发送
        # 发送图片

        image_path = os.path.abspath('test_human.png')
        self.bot.send_image_msg(recv["from"],image_path)
