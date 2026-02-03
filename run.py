"""
AI Agent Translator - 启动脚本

使用方法:
    python run.py

或者直接运行:
    python main.py
"""
import sys
import os

# 确保能正确导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import Main

if __name__ == '__main__':
    Main.main()
