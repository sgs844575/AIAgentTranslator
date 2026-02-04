"""
切换开关组件 - 现代化的开关控件
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen


class ToggleSwitch(QWidget):
    """
    切换开关组件
    
    特点：
    - 平滑的滑动动画
    - iOS风格设计
    - 支持标签文字
    
    信号：
    - toggled: 状态变化时发射
    """
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, label: str = "", checked: bool = False, 
                 parent=None):
        super().__init__(parent)
        self._checked = checked
        self._label_text = label
        self._animation = None
        
        self.setFixedSize(52, 32)
        self.setCursor(Qt.PointingHandCursor)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """初始化UI"""
        if self._label_text:
            # 如果有标签，创建水平布局
            self._main_widget = QWidget(self)
            self._main_widget.setFixedSize(52, 32)
            
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(12)
            
            self._label = QLabel(self._label_text)
            self._label.setStyleSheet("""
                font-size: 14px;
                color: #1D1D1F;
                background-color: transparent;
            """)
            layout.addWidget(self._label)
            layout.addWidget(self._main_widget)
            layout.addStretch()
            
            self.setFixedWidth(52 + 12 + self._label.sizeHint().width() + 20)
        
        # 滑块位置
        self._handle_pos = 28 if self._checked else 4
    
    def paintEvent(self, event):
        """绘制开关"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        bg_color = QColor("#34C759" if self._checked else "#E5E5EA")
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 52, 32, 16, 16)
        
        # 滑块阴影
        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        shadow_offset = 2
        painter.drawEllipse(
            int(self._handle_pos) + shadow_offset, 
            4 + shadow_offset, 
            20, 20
        )
        
        # 滑块
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(int(self._handle_pos), 4, 20, 20)
        
        painter.end()
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        self._checked = not self._checked
        self._animate()
        self.toggled.emit(self._checked)
        self.update()
    
    def _animate(self):
        """执行动画"""
        start_pos = 4 if not self._checked else 28
        end_pos = 28 if self._checked else 4
        
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        # 使用自定义属性动画
        self._handle_pos = start_pos
        
        # 创建帧动画
        def update_pos(frame):
            progress = frame / 10
            self._handle_pos = start_pos + (end_pos - start_pos) * progress
            self.update()
        
        import QTimer
        for i in range(11):
            QTimer.singleShot(i * 20, lambda f=i: update_pos(f))
    
    def isChecked(self) -> bool:
        """获取当前状态"""
        return self._checked
    
    def setChecked(self, checked: bool):
        """设置状态"""
        if self._checked != checked:
            self._checked = checked
            self._handle_pos = 28 if checked else 4
            self.update()
