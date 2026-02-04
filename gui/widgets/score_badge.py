"""
分数徽章组件 - 显示分数状态的彩色徽章
"""
from PyQt5.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ScoreBadge(QLabel):
    """
    分数徽章组件
    
    根据分数显示不同颜色的徽章
    - 90-100: 优秀（蓝色）
    - 80-89: 良好（绿色）
    - 70-79: 一般（橙色）
    - <70: 不及格（红色）
    
    使用示例：
        badge = ScoreBadge(85)
        badge.setScore(92)  # 更新分数
    """
    
    # 等级定义
    LEVELS = {
        'excellent': (90, 100, '#007AFF', '优秀'),  # 蓝色
        'good': (80, 89, '#34C759', '良好'),        # 绿色
        'fair': (70, 79, '#FF9500', '一般'),        # 橙色
        'poor': (0, 69, '#FF3B30', '需改进'),       # 红色
    }
    
    def __init__(self, score: int = 0, show_text: bool = True, parent=None):
        super().__init__(parent)
        self._score = score
        self._show_text = show_text
        self._setup_ui()
        self.setScore(score)
    
    def _setup_ui(self):
        """初始化UI"""
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(32)
        self.setMinimumWidth(70)
        
        # 添加阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def _get_level(self, score: int) -> tuple:
        """根据分数获取等级信息"""
        for level_info in self.LEVELS.values():
            min_score, max_score, color, label = level_info
            if min_score <= score <= max_score:
                return color, label
        return self.LEVELS['poor'][2], self.LEVELS['poor'][3]
    
    def _update_style(self):
        """更新样式"""
        color, label = self._get_level(self._score)
        
        if self._show_text:
            text = f"{self._score} {label}"
        else:
            text = str(self._score)
        
        self.setText(text)
        self.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: {color};
                border-radius: 16px;
                padding: 4px 12px;
                font-size: 13px;
                font-weight: 600;
            }}
        """)
    
    def setScore(self, score: int):
        """设置分数"""
        self._score = max(0, min(100, score))
        self._update_style()
    
    def score(self) -> int:
        """获取当前分数"""
        return self._score
    
    def setShowText(self, show: bool):
        """设置是否显示等级文字"""
        self._show_text = show
        self._update_style()
