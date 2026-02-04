"""
权重项组件 - 审核维度的权重设置项
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSpinBox,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class WeightItem(QWidget):
    """
    权重设置项组件
    
    特点：
    - 图标 + 名称 + 输入框的紧凑布局
    - 带颜色指示器的进度条效果
    - 实时显示权重占比
    
    信号：
    - valueChanged: 权重变化时发射
    """
    
    valueChanged = pyqtSignal(int)
    
    # 颜色方案
    COLORS = {
        'accuracy': ('#FF3B30', '#FFE5E5'),      # 红色系 - 准确性
        'technical': ('#FF9500', '#FFF4E5'),     # 橙色系 - 技术规范
        'terminology': ('#5856D6', '#E8E8FF'),   # 紫色系 - 术语一致性
        'language': ('#34C759', '#E5F9EB'),      # 绿色系 - 语言表达
        'format': ('#007AFF', '#E5F2FF'),        # 蓝色系 - 格式规范
    }
    
    ICONS = {
        'accuracy': '✓',
        'technical': '⚙️',
        'terminology': '📚',
        'language': '✍️',
        'format': '📋',
    }
    
    def __init__(self, weight_type: str, label: str, default_value: int = 20, 
                 max_value: int = 100, parent=None):
        super().__init__(parent)
        self._weight_type = weight_type
        self._label_text = label
        self._default_value = default_value
        self._max = max_value
        
        self._color, self._bg_color = self.COLORS.get(weight_type, ('#007AFF', '#E5F2FF'))
        self._icon = self.ICONS.get(weight_type, '•')
        
        self._setup_ui()
    
    def _setup_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 图标
        self.icon_label = QLabel(self._icon)
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                background-color: {self._bg_color};
                border-radius: 8px;
                color: {self._color};
            }}
        """)
        layout.addWidget(self.icon_label)
        
        # 名称
        self.name_label = QLabel(self._label_text)
        self.name_label.setStyleSheet("""
            font-size: 14px;
            color: #1D1D1F;
            font-weight: 500;
            background-color: transparent;
        """)
        layout.addWidget(self.name_label)
        
        # 权重条背景
        self.bar_container = QWidget()
        self.bar_container.setFixedHeight(8)
        self.bar_container.setStyleSheet("""
            background-color: #F2F2F7;
            border-radius: 4px;
        """)
        layout.addWidget(self.bar_container, 1)
        
        # 数值输入
        self.spin_box = QSpinBox()
        self.spin_box.setRange(0, self._max)
        self.spin_box.setValue(self._default_value)
        self.spin_box.setSuffix(" 分")
        self.spin_box.setFixedWidth(80)
        self.spin_box.setStyleSheet(f"""
            QSpinBox {{
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                font-weight: 600;
            }}
            QSpinBox:focus {{
                border-color: {self._color};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                background: transparent;
                border: none;
            }}
        """)
        self.spin_box.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.spin_box)
        
        # 初始化进度条
        self._update_bar(self._default_value)
    
    def _on_value_changed(self, value: int):
        """值变化处理"""
        self.valueChanged.emit(value)
        self._update_bar(value)
    
    def _update_bar(self, value: int):
        """更新进度条显示"""
        percentage = min(100, (value / self._max) * 100)
        self.bar_container.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self._color},
                stop:{percentage/100} {self._color},
                stop:{percentage/100+0.001} #F2F2F7,
                stop:1 #F2F2F7);
            border-radius: 4px;
        """)
    
    def value(self) -> int:
        """获取当前值"""
        return self.spin_box.value()
    
    def setValue(self, value: int):
        """设置值"""
        self.spin_box.setValue(value)
        self._update_bar(value)
