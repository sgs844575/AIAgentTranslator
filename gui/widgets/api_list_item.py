"""
API列表项组件 - 现代化的API列表项
"""
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class ApiListItem(QFrame):
    """
    API列表项组件
    
    显示API名称、启用状态和图标
    
    信号：
    - clicked: 点击时发射
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, api_id: str, name: str, icon: str = "🔌",
                 enabled: bool = True, parent=None):
        super().__init__(parent)
        self._api_id = api_id
        self._name = name
        self._icon = icon
        self._enabled = enabled
        self._selected = False
        
        self._setup_style()
        self._setup_ui()
        self.setCursor(Qt.PointingHandCursor)
    
    def _setup_style(self):
        """设置样式"""
        self.setFixedHeight(56)
        self._update_style()
    
    def _update_style(self):
        """更新样式（根据选中状态）"""
        if self._selected:
            self.setStyleSheet("""
                ApiListItem {
                    background-color: #007AFF;
                    border-radius: 12px;
                }
                QLabel {
                    color: white;
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                ApiListItem {
                    background-color: transparent;
                    border-radius: 12px;
                }
                ApiListItem:hover {
                    background-color: #F2F2F7;
                }
                QLabel {
                    color: #1D1D1F;
                    background-color: transparent;
                }
            """)
    
    def _setup_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # 状态指示器
        self.status_label = QLabel("●" if self._enabled else "○")
        self.status_label.setStyleSheet(f"""
            font-size: 10px;
            color: {'#34C759' if self._enabled else '#C7C7CC'};
            background-color: transparent;
        """)
        layout.addWidget(self.status_label)
        
        # 图标
        self.icon_label = QLabel(self._icon)
        self.icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.icon_label)
        
        # 名称
        self.name_label = QLabel(self._name)
        self.name_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 500;
        """)
        layout.addWidget(self.name_label)
        
        layout.addStretch()
        
        # 箭头
        self.arrow_label = QLabel("›")
        self.arrow_label.setStyleSheet("""
            font-size: 20px;
            color: #C7C7CC;
        """)
        layout.addWidget(self.arrow_label)
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        self.clicked.emit()
        super().mousePressEvent(event)
    
    def setSelected(self, selected: bool):
        """设置选中状态"""
        self._selected = selected
        self._update_style()
        if selected:
            self.arrow_label.setStyleSheet("""
                font-size: 20px;
                color: white;
                background-color: transparent;
            """)
        else:
            self.arrow_label.setStyleSheet("""
                font-size: 20px;
                color: #C7C7CC;
                background-color: transparent;
            """)
    
    def setEnabled(self, enabled: bool):
        """设置启用状态"""
        self._enabled = enabled
        self.status_label.setText("●" if enabled else "○")
        self.status_label.setStyleSheet(f"""
            font-size: 10px;
            color: {'#34C759' if enabled else '#C7C7CC'};
            background-color: transparent;
        """)
    
    def apiId(self) -> str:
        """获取API ID"""
        return self._api_id
    
    def name(self) -> str:
        """获取名称"""
        return self._name
