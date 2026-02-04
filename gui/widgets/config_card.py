"""
配置卡片组件 - 现代化的配置分组卡片
"""
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ConfigCard(QFrame):
    """
    现代化配置卡片
    
    特点：
    - 圆角设计
    - 柔和阴影
    - 清晰的标题区域
    - 内容区域自动扩展
    """
    
    def __init__(self, title: str = "", description: str = "", parent=None):
        super().__init__(parent)
        self._title_text = title
        self._description_text = description
        self._setup_style()
        self._setup_ui()
    
    def _setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            ConfigCard {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E5E5EA;
            }
        """)
        
        # 添加柔和阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def _setup_ui(self):
        """初始化UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        
        # 标题区域
        if self._title_text:
            self.header_layout = QVBoxLayout()
            self.header_layout.setSpacing(4)
            
            self.title_label = QLabel(self._title_text)
            self.title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: 600;
                color: #1D1D1F;
                background-color: transparent;
            """)
            self.header_layout.addWidget(self.title_label)
            
            if self._description_text:
                self.desc_label = QLabel(self._description_text)
                self.desc_label.setStyleSheet("""
                    font-size: 13px;
                    color: #86868B;
                    background-color: transparent;
                """)
                self.header_layout.addWidget(self.desc_label)
            
            self.main_layout.addLayout(self.header_layout)
        
        # 内容区域
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        self.main_layout.addLayout(self.content_layout, 1)
    
    def add_widget(self, widget):
        """添加控件到内容区域"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加布局到内容区域"""
        self.content_layout.addLayout(layout)
    
    def set_title(self, title: str):
        """设置标题"""
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)
    
    def set_description(self, description: str):
        """设置描述"""
        if hasattr(self, 'desc_label'):
            self.desc_label.setText(description)
