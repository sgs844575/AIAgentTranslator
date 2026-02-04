"""
快速开始页面 - 现代化的欢迎界面
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from gui.widgets import StepCard


class QuickStartPage(QWidget):
    """
    快速开始页面（现代化版本）
    
    职责：
    - 展示欢迎信息
    - 引导用户完成初始配置
    - 提供快速导航入口
    
    信号：
    - nav_requested: 请求导航到指定页面
    """
    
    nav_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置现代化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setAlignment(Qt.AlignCenter)
        
        # ========== 欢迎区域 ==========
        welcome_container = QWidget()
        welcome_layout = QVBoxLayout(welcome_container)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setSpacing(16)
        
        # Logo图标
        logo = QLabel("🤖")
        logo.setStyleSheet("font-size: 72px;")
        logo.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(logo)
        
        # 主标题
        title = QLabel("欢迎使用")
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: 700;
            color: #1D1D1F;
            background-color: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(title)
        
        # 应用名称
        app_name = QLabel("AI Agent Translator")
        app_name.setStyleSheet("""
            font-size: 32px;
            font-weight: 600;
            color: #007AFF;
            background-color: transparent;
        """)
        app_name.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(app_name)
        
        # 副标题
        subtitle = QLabel("基于多Agent协作的智能翻译工具")
        subtitle.setStyleSheet("""
            font-size: 18px;
            color: #86868B;
            background-color: transparent;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(subtitle)
        
        # 描述文字
        desc = QLabel(
            "四位专家协同工作：原语言分析 → 翻译 → 审核 → 优化\n"
            "为您提供高质量的机器翻译体验"
        )
        desc.setStyleSheet("""
            font-size: 14px;
            color: #8E8E93;
            line-height: 1.6;
            background-color: transparent;
        """)
        desc.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(desc)
        
        layout.addWidget(welcome_container)
        layout.addSpacing(40)
        
        # ========== 步骤卡片区域 ==========
        steps_container = QWidget()
        steps_layout = QHBoxLayout(steps_container)
        steps_layout.setSpacing(24)
        steps_layout.setAlignment(Qt.AlignCenter)
        
        steps = [
            {
                "number": 1,
                "title": "配置接口",
                "description": "添加您的API密钥\n连接翻译服务",
                "page": "api_manager",
                "color": "#007AFF"
            },
            {
                "number": 2,
                "title": "设置参数",
                "description": "调整翻译参数\n优化输出效果",
                "page": "translation_settings",
                "color": "#34C759"
            },
            {
                "number": 3,
                "title": "开始翻译",
                "description": "输入原文内容\n获取智能翻译",
                "page": "translate",
                "color": "#FF9500"
            }
        ]
        
        for step in steps:
            card = StepCard(
                step_number=step["number"],
                title=step["title"],
                description=step["description"],
                accent_color=step["color"]
            )
            card.clicked.connect(
                lambda p=step["page"]: self.nav_requested.emit(p)
            )
            steps_layout.addWidget(card)
        
        layout.addWidget(steps_container)
        
        # ========== 底部提示 ==========
        layout.addSpacing(30)
        
        footer = QLabel("点击上方卡片开始配置，或从左侧导航栏进入各功能页面")
        footer.setStyleSheet("""
            font-size: 13px;
            color: #C7C7CC;
            background-color: transparent;
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        layout.addStretch()
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
