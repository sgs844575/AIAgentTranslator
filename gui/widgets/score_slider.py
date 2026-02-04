"""
分数滑块组件 - 带视觉反馈的分数选择器
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QSlider, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class ScoreSlider(QWidget):
    """
    分数滑块组件
    
    特点：
    - 实时显示当前分数
    - 颜色根据分数变化（低分红色、中等黄色、高分绿色）
    - 滑块轨道带有渐变效果
    - 支持自定义范围
    
    信号：
    - valueChanged: 分数变化时发射
    """
    
    valueChanged = pyqtSignal(int)
    
    # 分数颜色映射
    COLOR_LOW = "#FF3B30"      # 60-70: 红色
    COLOR_MEDIUM = "#FF9500"   # 70-85: 橙色
    COLOR_GOOD = "#34C759"     # 85-95: 绿色
    COLOR_EXCELLENT = "#007AFF"  # 95+: 蓝色
    
    def __init__(self, min_value: int = 60, max_value: int = 95, 
                 default_value: int = 80, suffix: str = "分", parent=None):
        super().__init__(parent)
        self._min = min_value
        self._max = max_value
        self._suffix = suffix
        self._current_value = default_value
        
        self._setup_ui()
        self._update_display()
    
    def _setup_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(self._min, self._max)
        self.slider.setValue(self._current_value)
        self.slider.setStyleSheet(self._get_slider_style())
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider, 1)
        
        # 分数显示标签
        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setFixedSize(70, 36)
        self.score_label.setStyleSheet(self._get_label_style())
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self.score_label)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.score_label.setGraphicsEffect(shadow)
        
        layout.addWidget(self.score_label)
    
    def _get_slider_style(self) -> str:
        """获取滑块样式"""
        return """
            QSlider::groove:horizontal {
                height: 8px;
                background: #E5E5EA;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF3B30,
                    stop:0.33 #FF9500,
                    stop:0.66 #34C759,
                    stop:1 #007AFF);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 20px;
                height: 20px;
                margin: -6px 0;
                background: white;
                border: 2px solid #007AFF;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #007AFF;
            }
        """
    
    def _get_label_style(self) -> str:
        """获取标签样式（根据当前值）"""
        color = self._get_color_for_score(self._current_value)
        return f"""
            QLabel {{
                font-size: 16px;
                font-weight: 700;
                color: white;
                background-color: {color};
                border-radius: 10px;
                padding: 4px 8px;
            }}
        """
    
    def _get_color_for_score(self, score: int) -> str:
        """根据分数获取对应颜色"""
        if score >= 95:
            return self.COLOR_EXCELLENT
        elif score >= 85:
            return self.COLOR_GOOD
        elif score >= 70:
            return self.COLOR_MEDIUM
        else:
            return self.COLOR_LOW
    
    def _on_value_changed(self, value: int):
        """滑块值变化处理"""
        self._current_value = value
        self._update_display()
        self.valueChanged.emit(value)
    
    def _update_display(self):
        """更新显示"""
        self.score_label.setText(f"{self._current_value}{self._suffix}")
        self.score_label.setStyleSheet(self._get_label_style())
    
    def value(self) -> int:
        """获取当前值"""
        return self._current_value
    
    def setValue(self, value: int):
        """设置值"""
        self.slider.setValue(value)
    
    def setRange(self, min_value: int, max_value: int):
        """设置范围"""
        self._min = min_value
        self._max = max_value
        self.slider.setRange(min_value, max_value)
