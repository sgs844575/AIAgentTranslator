"""
现代化按钮组件 - macOS风格的按钮
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt


class ModernButton(QPushButton):
    """
    现代化按钮
    
    支持两种类型：
    - Primary: 蓝色填充主按钮
    - Secondary: 灰色描边次按钮
    
    特点：
    - 圆角设计
    - 悬停效果
    - 点击反馈
    """
    
    def __init__(self, text: str = "", primary: bool = True, 
                 icon: str = "", parent=None):
        super().__init__(text, parent)
        self._primary = primary
        self._icon = icon
        if icon:
            self.setText(f"{icon} {text}" if text else icon)
        self._setup_style()
    
    def _setup_style(self):
        """设置样式"""
        if self._primary:
            self.setStyleSheet("""
                ModernButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                }
                ModernButton:hover {
                    background-color: #0056CC;
                }
                ModernButton:pressed {
                    background-color: #004494;
                }
                ModernButton:disabled {
                    background-color: #B8D4F0;
                }
            """)
        else:
            self.setStyleSheet("""
                ModernButton {
                    background-color: #F2F2F7;
                    color: #007AFF;
                    border: 1px solid #D1D1D6;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                }
                ModernButton:hover {
                    background-color: #E5E5EA;
                }
                ModernButton:pressed {
                    background-color: #D1D1D6;
                }
                ModernButton:disabled {
                    color: #8E8E93;
                    border-color: #E5E5EA;
                }
            """)
    
    def setPrimary(self, primary: bool):
        """设置按钮类型"""
        self._primary = primary
        self._setup_style()
