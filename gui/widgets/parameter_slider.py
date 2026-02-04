"""
参数滑块组件 - 带数值显示的现代化滑块
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class ParameterSlider(QWidget):
    """
    参数滑块组件
    
    特点：
    - 标签 + 滑块 + 数值显示
    - 可自定义数值格式
    - 彩色轨道
    - 可选描述文字
    
    信号：
    - valueChanged: 值变化时发射
    """
    
    valueChanged = pyqtSignal(float)
    
    def __init__(self, label: str = "", min_value: float = 0, max_value: float = 1,
                 default_value: float = 0.5, decimals: int = 2, 
                 description: str = "", color: str = "#007AFF", parent=None):
        super().__init__(parent)
        self._label_text = label
        self._min = min_value
        self._max = max_value
        self._decimals = decimals
        self._multiplier = 10 ** decimals
        self._color = color
        self._description = description
        
        self._setup_ui()
        self.setValue(default_value)
    
    def _setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标签行
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        self.label = QLabel(self._label_text)
        self.label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #1D1D1F;
            background-color: transparent;
        """)
        header_layout.addWidget(self.label)
        
        header_layout.addStretch()
        
        # 数值显示
        self.value_label = QLabel()
        self.value_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {self._color};
            background-color: {self._color}20;
            border-radius: 6px;
            padding: 4px 10px;
            min-width: 50px;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        
        # 数值标签阴影
        shadow = QGraphicsDropShadowEffect(self.value_label)
        shadow.setBlurRadius(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 1)
        self.value_label.setGraphicsEffect(shadow)
        
        header_layout.addWidget(self.value_label)
        layout.addLayout(header_layout)
        
        # 滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(
            int(self._min * self._multiplier),
            int(self._max * self._multiplier)
        )
        self.slider.setStyleSheet(self._get_slider_style())
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)
        
        # 描述文字
        if self._description:
            self.desc_label = QLabel(self._description)
            self.desc_label.setStyleSheet("""
                font-size: 12px;
                color: #86868B;
                background-color: transparent;
            """)
            layout.addWidget(self.desc_label)
    
    def _get_slider_style(self) -> str:
        """获取滑块样式"""
        return f"""
            QSlider::groove:horizontal {{
                height: 8px;
                background: #E5E5EA;
                border-radius: 4px;
            }}
            QSlider::sub-page:horizontal {{
                height: 8px;
                background: {self._color};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                width: 20px;
                height: 20px;
                margin: -6px 0;
                background: white;
                border: 2px solid {self._color};
                border-radius: 10px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {self._color};
            }}
        """
    
    def _on_slider_changed(self, value: int):
        """滑块值变化处理"""
        float_value = value / self._multiplier
        self._update_display(float_value)
        self.valueChanged.emit(float_value)
    
    def _update_display(self, value: float):
        """更新数值显示"""
        format_str = f"{{:.{self._decimals}f}}"
        self.value_label.setText(format_str.format(value))
    
    def value(self) -> float:
        """获取当前值"""
        return self.slider.value() / self._multiplier
    
    def setValue(self, value: float):
        """设置值"""
        self.slider.setValue(int(value * self._multiplier))
        self._update_display(value)
