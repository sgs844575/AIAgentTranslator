"""
步骤卡片组件 - 快速开始页面的步骤展示卡片
"""
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class StepCard(QFrame):
    """
    步骤卡片组件
    
    用于快速开始页面，展示步骤序号、标题、描述和操作按钮
    
    信号：
    - clicked: 点击卡片时发射
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, step_number: int, title: str, description: str,
                 accent_color: str = "#007AFF", parent=None):
        super().__init__(parent)
        self._step = step_number
        self._title = title
        self._description = description
        self._accent_color = accent_color
        
        self._setup_style()
        self._setup_ui()
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
    
    def _setup_style(self):
        """设置样式"""
        self.setFixedSize(220, 260)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            StepCard {{
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E5E5EA;
            }}
            StepCard:hover {{
                border-color: {self._accent_color};
                background-color: #FAFAFA;
            }}
        """)
        
        # 添加阴影
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(20)
        self._shadow.setColor(QColor(0, 0, 0, 25))
        self._shadow.setOffset(0, 4)
        self.setGraphicsEffect(self._shadow)
    
    def _setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 28, 24, 24)
        layout.setSpacing(12)
        
        # 步骤序号圆形标签
        self.num_label = QLabel(str(self._step))
        self.num_label.setFixedSize(48, 48)
        self.num_label.setAlignment(Qt.AlignCenter)
        self.num_label.setStyleSheet(f"""
            background-color: {self._accent_color};
            color: white;
            border-radius: 24px;
            font-size: 20px;
            font-weight: 700;
        """)
        layout.addWidget(self.num_label, alignment=Qt.AlignCenter)
        
        # 标题
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #1D1D1F;
            background-color: transparent;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 描述
        self.desc_label = QLabel(self._description)
        self.desc_label.setStyleSheet("""
            font-size: 13px;
            color: #86868B;
            line-height: 1.5;
            background-color: transparent;
        """)
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.desc_label)
        
        layout.addStretch()
        
        # 操作提示
        self.action_label = QLabel("点击开始 →")
        self.action_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {self._accent_color};
            background-color: transparent;
        """)
        self.action_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.action_label)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """鼠标进入"""
        self._shadow.setBlurRadius(30)
        self._shadow.setColor(QColor(0, 0, 0, 40))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开"""
        self._shadow.setBlurRadius(20)
        self._shadow.setColor(QColor(0, 0, 0, 25))
        super().leaveEvent(event)
    
    def setStepNumber(self, number: int):
        """设置步骤序号"""
        self._step = number
        self.num_label.setText(str(number))
    
    def setAccentColor(self, color: str):
        """设置主题色"""
        self._accent_color = color
        self._setup_style()
