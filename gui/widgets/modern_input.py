"""
现代化输入框组件
"""
from PyQt5.QtWidgets import QLineEdit, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ModernInput(QLineEdit):
    """
    现代化输入框
    
    特点：
    - 圆角设计
    - 聚焦时蓝色边框
    - 可选阴影效果
    - 支持密码模式
    """
    
    def __init__(self, placeholder: str = "", password: bool = False, 
                 show_shadow: bool = False, parent=None):
        super().__init__(parent)
        self._placeholder = placeholder
        self._password = password
        self._show_shadow = show_shadow
        
        self.setPlaceholderText(placeholder)
        if password:
            self.setEchoMode(QLineEdit.Password)
        
        self._setup_style()
    
    def _setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            ModernInput {
                background-color: white;
                border: 1px solid #D1D1D6;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                color: #1D1D1F;
                selection-background-color: #007AFF;
            }
            ModernInput:focus {
                border-color: #007AFF;
                background-color: white;
            }
            ModernInput::placeholder {
                color: #8E8E93;
            }
        """)
        
        if self._show_shadow:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 20))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)
    
    def setPasswordMode(self, enabled: bool):
        """设置密码模式"""
        self.setEchoMode(QLineEdit.Password if enabled else QLineEdit.Normal)
