import json

from utils import SingleIndentEncoder


def read_json_file(file_path):
    """读取JSON文件"""
    check_and_create_file(file_path, content="{}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 不是有效的JSON格式")
        return None


def write_json_file(file_path, data, indent=4, ensure_ascii=False, cls=None):
    """写入JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, cls=SingleIndentEncoder.CustomJSONEncoder)
        return True
    except IOError as e:
        print(f"写入文件时出错: {e}")
        return False


def read_txt_file(file_path):
    """读取TXT文件"""
    check_and_create_file(file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return None


def write_txt_file(file_path, content, mode='w'):
    """写入TXT文件
    mode: 'w' 覆盖写入, 'a' 追加写入
    """
    try:
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"写入文件时出错: {e}")
        return False


import os


def check_and_create_file(file_path, content=""):
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 确保目录存在（如果路径包含目录）
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # 创建文件并写入内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return True
    except Exception as e:
        print(f"错误: 无法创建文件 '{file_path}' ({e})")
        return False

def get_all_files(directory, suffix):
    """
    获取目录及其子目录下所有 .txt 文件路径
    :param directory: 目标目录路径（如 "./data"）
    :return: 包含所有.txt文件路径的列表
    """
    txt_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(f".{suffix}"):
                txt_files.append(os.path.join(root, file))
    return txt_files
