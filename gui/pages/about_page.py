"""
关于页面 - 现代化的应用信息界面
"""
import webbrowser

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from gui.widgets import ModernButton


class AboutPage(QWidget):
    """
    关于页面（现代化版本）
    
    职责：
    - 展示应用信息
    - 显示版本号
    - 提供链接入口
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置现代化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)
        
        # ========== 主卡片 ==========
        card = QWidget()
        card.setFixedSize(480, 560)
        card.setStyleSheet("""
            background-color: white;
            border-radius: 24px;
        """)
        
        # 添加阴影
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(48, 48, 48, 48)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)
        
        # Logo
        logo = QLabel("🤖")
        logo.setStyleSheet("font-size: 80px;")
        logo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(logo)
        
        # 应用名称
        title = QLabel("AI Agent Translator")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #1D1D1F;
            background-color: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # 版本号
        version = QLabel("版本 2.0.0")
        version.setStyleSheet("""
            font-size: 15px;
            color: #86868B;
            background-color: transparent;
        """)
        version.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(version)
        
        # 分隔线
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #E5E5EA;")
        separator.setMaximumWidth(200)
        card_layout.addWidget(separator)
        
        # 描述
        desc = QLabel(
            "基于多Agent协作的智能翻译工具\n"
            "四位专家协同，为您提供高质量翻译"
        )
        desc.setStyleSheet("""
            font-size: 14px;
            color: #3C3C43;
            line-height: 1.6;
            background-color: transparent;
        """)
        desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc)
        
        # 特性列表
        features = QLabel(
            "✦ 原语言分析专家\n"
            "✦ 翻译专家\n"
            "✦ 翻译审核专家\n"
            "✦ 翻译优化专家"
        )
        features.setStyleSheet("""
            font-size: 13px;
            color: #8E8E93;
            line-height: 1.8;
            background-color: transparent;
        """)
        features.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(features)
        
        card_layout.addStretch()
        
        # GitHub按钮
        github_btn = ModernButton("🐙 GitHub", primary=False)
        github_btn.setFixedSize(140, 44)
        github_btn.clicked.connect(self._open_github)
        card_layout.addWidget(github_btn, alignment=Qt.AlignCenter)
        
        # 版权信息
        copyright = QLabel("© 2024 AI Agent Translator. All rights reserved.")
        copyright.setStyleSheet("""
            font-size: 12px;
            color: #C7C7CC;
            background-color: transparent;
        """)
        copyright.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(copyright)
        
        layout.addWidget(card)
        layout.addStretch()
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
    
    def _open_github(self):
        """打开GitHub仓库"""
        webbrowser.open("https://github.com/sgs844575/AIAgentTranslator")
