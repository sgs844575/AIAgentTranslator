import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 预编译正则表达式（全局常量）
JAPANESE_CHAR_PATTERN = re.compile(
    r'(?![゛゜っー])'
    r'[\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF\uFF65-\uFF9F]'
)
JAPANESE_EXTRACT_PATTERN = re.compile(
    r'(?![゛゜っー])'
    r'[\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF\uFF65-\uFF9F]+'
)

# 创建可重用的TF-IDF向量化器（避免重复实例化）
VECTORIZER = TfidfVectorizer()

# 转义映射表（全局常量）
ESCAPE_MAP = {
    "\n": "<b_n>",
    "\\n": "<b_b>",
    "\r": "<b_r>",
    "　": "<b_q>",
    "<br>": "<b_a>",
    "\"": "<quote>",
    # "、": "<symbol_abb>",
    # "♥": "<symbol_cbb>"
}

# 反转义映射表（全局常量）
UNESCAPE_MAP = {
    "<b_n>": "\n",
    "<b_b>": "\\n",
    "<b_r>": "\r",
    "<b_q>": "　",
    "<b_a>": "<br>",
    "<quote>": "\"",
    # "<symbol_abb>": "、",
    # "<symbol_cbb>": "♥",
    "，": "、",
    "......": "……",
    "...": "……",
    "·": "・"
}
# 添加清理标签（这些标签会被替换为空字符串）
CLEANUP_TAGS = {"</b_n>", "</b_r>", "</b_q>", "</b_a>", "</b>", "</symbol_abb>", "</symbol_b>", "</symbol_cbb>"}


def contains_japanese(text: str) -> bool:
    """检查文本是否包含日文字符"""
    return bool(JAPANESE_CHAR_PATTERN.search(text))


def extract_japanese(text: str) -> str:
    """提取文本中的日文字符"""
    return ''.join(JAPANESE_EXTRACT_PATTERN.findall(text))


def similarity(sentence1: str, sentence2: str) -> float:
    """计算两个句子的余弦相似度（优化异常处理）"""
    # 快速检查相同句子
    if sentence1 == sentence2:
        return 1.0

    # 处理空值情况
    if not (sentence1 and sentence2):
        return 0.0

    try:
        tfidf_matrix = VECTORIZER.fit_transform([sentence1, sentence2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:  # 只捕获预期的异常
        return 0.0


def escape_special_characters(text: str) -> str:
    """转义特殊字符（使用映射表优化）"""
    for char, replacement in ESCAPE_MAP.items():
        text = text.replace(char, replacement)
    return text


def unescape_special_characters(text: str) -> str:
    """反转义特殊字符（分步优化处理）"""
    # 第一步：清理无用标签
    for tag in CLEANUP_TAGS:
        text = text.replace(tag, "")

    # 第二步：执行主要反转义
    for replacement, char in UNESCAPE_MAP.items():
        text = text.replace(replacement, char)

    return text
