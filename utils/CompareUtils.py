import re
from collections import Counter

from utils import FileUtils


def count_punctuation_and_tags(text):
    """
    统计文本中的标点符号和特定标签的数量
    :param text: 输入文本字符串
    :return: 包含标点符号和标签计数的字典
    """
    # 中文标点符号
    text = text.replace("々","").replace("～","").replace("译文的符号或标签与原文无法对应，请重新翻译<b_n>", "")
    chinese_punctuation = r'[\u3001-\u303f\uff00-\uffef，。、；：？！「」『』（）《》【】―]'
    # 英文标点符号
    english_punctuation = r'[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}]'
    # 常见HTML/XML标签
    tags = r'<\/?\w+[^>]*>'

    # 统计中文标点
    chn_punct = Counter(re.findall(chinese_punctuation, text))
    # 统计英文标点
    eng_punct = Counter(re.findall(english_punctuation, text))
    # 统计标签
    tag_count = Counter(re.findall(tags, text))

    # 合并结果
    result = {
        'chinese_punctuation': dict(chn_punct),
        'english_punctuation': dict(eng_punct),
        'tags': dict(tag_count)
    }
    return result


def compare_punctuation_and_tags(text1, text2):
    """
    比较两个文本的标点符号和标签数量是否相同
    :param text1: 第一个文本
    :param text2: 第二个文本
    :return: 布尔值，表示是否相同
    """
    count1 = count_punctuation_and_tags(text1)
    count2 = count_punctuation_and_tags(text2)

    # 比较中英文标点和标签数量是否完全相同
    return (
            count1['chinese_punctuation'] == count2['chinese_punctuation'] and
            count1['english_punctuation'] == count2['english_punctuation'] and
            count1['tags'] == count2['tags']
    )
