"""
AI Agent Translator
基于多Agent协作的智能翻译工具

四位专家协同工作：
1. 原语言分析专家 - 分析原文语言特征
2. 翻译专家 - 进行高质量翻译
3. 翻译审核专家 - 审核翻译质量
4. 翻译优化专家 - 润色和优化译文
"""
import sys
import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui import MainWindow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("启动 AI Agent Translator...")
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("AI Agent Translator")
    app.setApplicationVersion("2.0.0")
    
    # 设置应用字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)
    
    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("应用启动成功")
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
