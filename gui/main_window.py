"""
AI Agent Translator 主窗口 - macOS 风格设计 (修复版)
"""
import sys
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional, List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTextEdit, QPushButton, QLabel, QSlider, QFrame,
    QSplitter, QComboBox, QCheckBox, QProgressBar, QMessageBox,
    QGroupBox, QScrollArea, QSpinBox, QStackedWidget, QLineEdit,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QTextBrowser, QListWidget,
    QListWidgetItem, QGraphicsDropShadowEffect, QSizePolicy,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import (
    Qt, QThreadPool, pyqtSignal, QObject, QSize, QTimer,
    QPropertyAnimation, QEasingCurve, QPoint
)
from PyQt5.QtGui import (
    QFont, QIcon, QColor, QPalette, QPainter, QBrush,
    QLinearGradient, QCursor
)

from core import TranslationPipeline, TranslationOptions
from models import TranslationContext, AgentStatus
from utils import FileUtils
from gui.agent_panel import AgentPanel
from gui.pages import (
    ReviewerConfigPage,
    TranslationSettingsPage,
    ApiManagerPage,
    QuickStartPage,
    AboutPage
)

logger = logging.getLogger(__name__)


# ==================== macOS 风格组件 ====================

class MacButton(QPushButton):
    """macOS 风格按钮"""
    
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self._setup_style()
    
    def _setup_style(self):
        if self.primary:
            self.setStyleSheet("""
                MacButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 500;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                }
                MacButton:hover {
                    background-color: #0056CC;
                }
                MacButton:pressed {
                    background-color: #004494;
                }
                MacButton:disabled {
                    background-color: #B8D4F0;
                }
            """)
        else:
            self.setStyleSheet("""
                MacButton {
                    background-color: #E8E8ED;
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 500;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                }
                MacButton:hover {
                    background-color: #D1D1D6;
                }
                MacButton:pressed {
                    background-color: #BFBFBF;
                }
            """)


class MacCard(QFrame):
    """macOS 风格卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self._setup_shadow()
    
    def _setup_style(self):
        self.setStyleSheet("""
            MacCard {
                background-color: rgba(255, 255, 255, 0.90);
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.06);
            }
        """)
    
    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class MacSidebar(QFrame):
    """macOS 风格侧边栏"""
    
    nav_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.items = {}
        self.current_item = None
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            MacSidebar {
                background-color: #F5F5F7;
                border-right: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(4)
        
        # Logo
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(12, 8, 12, 8)
        
        logo_icon = QLabel("🤖")
        logo_icon.setStyleSheet("font-size: 24px;")
        logo_layout.addWidget(logo_icon)
        
        logo_text = QLabel("AI Translator")
        logo_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #1D1D1F;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
        """)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        
        layout.addWidget(logo_container)
        layout.addSpacing(20)
        
        # 快速开始
        self.quick_start = self._create_nav_item("⚡", "快速开始", "quick_start")
        layout.addWidget(self.quick_start)
        layout.addSpacing(10)
        
        # 翻译组
        self._add_nav_group("翻译", [
            ("▶️", "开始翻译", "translate"),
            ("📊", "任务结果", "results"),
        ])
        
        # 配置组
        self._add_nav_group("配置", [
            ("🔌", "接口管理", "api_manager"),
            ("⚙️", "翻译设置", "translation_settings"),
            ("🔍", "审核配置", "reviewer_config"),
        ])
        
        # 数据组
        self._add_nav_group("数据", [
            ("📚", "术语表", "glossary"),
            ("🚫", "禁翻表", "blocked_terms"),
        ])
        
        layout.addStretch()
        
        # 关于
        self.about_item = self._create_nav_item("ℹ️", "关于", "about")
        layout.addWidget(self.about_item)
    
    def _add_nav_group(self, title, items):
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #86868B;
            padding: 8px 12px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
        """)
        self.layout().addWidget(title_label)
        
        for icon, text, item_id in items:
            item = self._create_nav_item(icon, text, item_id)
            self.layout().addWidget(item)
            self.items[item_id] = item
        
        self.layout().addSpacing(8)
    
    def _create_nav_item(self, icon, text, item_id):
        item = QFrame()
        item.setFixedHeight(36)
        item.setCursor(QCursor(Qt.PointingHandCursor))
        item.item_id = item_id
        item.is_selected = False
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 15px;")
        layout.addWidget(icon_label)
        
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            font-size: 13px;
            color: #1D1D1F;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
        """)
        layout.addWidget(text_label)
        layout.addStretch()
        
        item.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
        """)
        
        item.mousePressEvent = lambda e, i=item: self._on_item_clicked(i)
        return item
    
    def _on_item_clicked(self, item):
        # 避免重复点击同一项
        if self.current_item == item:
            return
            
        if self.current_item:
            self._set_item_selected(self.current_item, False)
        
        self._set_item_selected(item, True)
        self.current_item = item
        self.nav_clicked.emit(item.item_id)
    
    def _set_item_selected(self, item, selected):
        if selected:
            item.setStyleSheet("""
                QFrame {
                    background-color: #007AFF;
                    border-radius: 8px;
                }
            """)
            for label in item.findChildren(QLabel):
                if label.text() not in ["▶️", "📊", "🔌", "⚙️", "🔍", "📚", "🚫", "ℹ️", "⚡", "🤖"]:
                    label.setStyleSheet("""
                        font-size: 13px;
                        color: white;
                        font-weight: 500;
                    """)
        else:
            item.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: rgba(0, 0, 0, 0.04);
                }
            """)
            for label in item.findChildren(QLabel):
                if label.text() not in ["▶️", "📊", "🔌", "⚙️", "🔍", "📚", "🚫", "ℹ️", "⚡", "🤖"]:
                    label.setStyleSheet("""
                        font-size: 13px;
                        color: #1D1D1F;
                    """)
    
    def set_selected(self, item_id):
        """仅更新UI选中状态，不触发信号（用于程序导航）"""
        item = None
        if item_id in self.items:
            item = self.items[item_id]
        elif item_id == "quick_start" and hasattr(self, 'quick_start'):
            item = self.quick_start
        elif item_id == "about" and hasattr(self, 'about_item'):
            item = self.about_item
        
        if item and item != self.current_item:
            if self.current_item:
                self._set_item_selected(self.current_item, False)
            self._set_item_selected(item, True)
            self.current_item = item


# ==================== 动画页面基类 ====================

class AnimatedPage(QWidget):
    """带动画的页面基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity_effect = None
        self._animation = None
    
    def fade_in(self):
        """淡入动画"""
        # 清理之前的动画
        if self._animation:
            self._animation.stop()
            self._animation = None
        
        # 创建或获取透明度效果
        if not self._opacity_effect:
            self._opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self._opacity_effect)
        
        self._opacity_effect.setOpacity(0.0)
        
        # 创建新动画
        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setDuration(300)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 动画完成后清理 effect，避免影响对话框
        self._animation.finished.connect(self._clear_opacity_effect)
        
        self._animation.start()
    
    def _clear_opacity_effect(self):
        """动画完成后清理透明度效果，避免影响对话框"""
        # 清除 graphics effect，这样不会影响子对话框
        self.setGraphicsEffect(None)
        self._opacity_effect = None
        self._animation = None
    
    def showEvent(self, event):
        super().showEvent(event)
        # 延迟一点执行动画，确保widget已经准备好
        QTimer.singleShot(50, self.fade_in)


# ==================== 页面类 ====================

class TranslatePage(AnimatedPage):
    """翻译页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 页面标题
        header = QHBoxLayout()
        title = QLabel("开始翻译")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #1D1D1F;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # 主内容区 - 使用水平分割器
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(1)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E5E5E5;
            }
        """)
        
        # ==================== 左侧：翻译区域 ====================
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setStyleSheet("background-color: transparent;")
        
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: transparent;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 12, 0)
        left_layout.setSpacing(16)
        
        # 原文卡片
        src_card = MacCard()
        src_card.setMinimumHeight(280)
        src_layout = QVBoxLayout(src_card)
        src_layout.setContentsMargins(16, 16, 16, 16)
        src_layout.setSpacing(12)
        
        src_header = QHBoxLayout()
        src_title = QLabel("📄 原文")
        src_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1D1D1F;")
        src_header.addWidget(src_title)
        src_header.addStretch()
        
        self.clear_src_btn = MacButton("清空", primary=False)
        self.clear_src_btn.setFixedSize(60, 28)
        src_header.addWidget(self.clear_src_btn)
        src_layout.addLayout(src_header)
        
        self.src_text = QTextEdit()
        self.src_text.setPlaceholderText("请输入要翻译的内容...")
        self.src_text.setAcceptRichText(False)
        self.src_text.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #E5E5E5;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
            }
            QTextEdit:focus {
                border-color: #007AFF;
                background-color: white;
            }
        """)
        src_layout.addWidget(self.src_text, 1)
        
        left_layout.addWidget(src_card, 1)
        
        # 译文卡片
        trans_card = MacCard()
        trans_card.setMinimumHeight(280)
        trans_layout = QVBoxLayout(trans_card)
        trans_layout.setContentsMargins(16, 16, 16, 16)
        trans_layout.setSpacing(12)
        
        trans_header = QHBoxLayout()
        trans_title = QLabel("✨ 译文")
        trans_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1D1D1F;")
        trans_header.addWidget(trans_title)
        trans_header.addStretch()
        
        self.copy_btn = MacButton("复制", primary=False)
        self.copy_btn.setFixedSize(70, 28)
        trans_header.addWidget(self.copy_btn)
        
        self.clear_trans_btn = MacButton("清空", primary=False)
        self.clear_trans_btn.setFixedSize(70, 28)
        trans_header.addWidget(self.clear_trans_btn)
        trans_layout.addLayout(trans_header)
        
        self.trans_text = QTextEdit()
        self.trans_text.setPlaceholderText("翻译结果将显示在这里...")
        self.trans_text.setReadOnly(True)
        self.trans_text.setAcceptRichText(False)
        self.trans_text.setStyleSheet("""
            QTextEdit {
                background-color: #F0F9FF;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        trans_layout.addWidget(self.trans_text, 1)
        
        left_layout.addWidget(trans_card, 1)
        left_layout.addStretch(0)
        
        left_scroll.setWidget(left_widget)
        content_splitter.addWidget(left_scroll)
        
        # ==================== 右侧：状态面板 ====================
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_scroll.setStyleSheet("background-color: transparent;")
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: transparent;")
        right_widget.setMinimumWidth(340)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(12, 0, 0, 0)
        right_layout.setSpacing(16)
        
        # Agent面板卡片 - 使用固定高度，不占用额外空间
        agent_card = MacCard()
        agent_card.setMinimumHeight(420)
        agent_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        agent_layout = QVBoxLayout(agent_card)
        agent_layout.setContentsMargins(12, 12, 12, 12)
        agent_layout.setSpacing(8)
        
        agent_title = QLabel("🤖 Agent状态")
        agent_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1D1D1F;")
        agent_layout.addWidget(agent_title)
        
        self.agent_panel = AgentPanel()
        self.agent_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        agent_layout.addWidget(self.agent_panel)
        right_layout.addWidget(agent_card)
        
        # 执行详情卡片 - 可伸缩高度，占满剩余空间
        details_card = MacCard()
        details_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(12, 12, 12, 12)
        details_layout.setSpacing(8)
        
        details_title = QLabel("📝 执行详情")
        details_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1D1D1F;")
        details_layout.addWidget(details_title)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                font-family: monospace;
            }
        """)
        details_layout.addWidget(self.details_text, 1)
        right_layout.addWidget(details_card)
        
        right_layout.addStretch(0)
        right_scroll.setWidget(right_widget)
        content_splitter.addWidget(right_scroll)
        
        # 设置分割比例 - 左侧占更多空间
        content_splitter.setSizes([600, 380])
        
        layout.addWidget(content_splitter, 1)
        
        # 底部按钮区
        bottom_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #E5E5E5;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 4px;
            }
        """)
        bottom_layout.addWidget(self.progress_bar, 1)
        
        bottom_layout.addStretch()
        
        self.stop_btn = MacButton("⏹ 停止翻译", primary=False)
        self.stop_btn.setFixedSize(140, 44)
        self.stop_btn.setVisible(False)
        bottom_layout.addWidget(self.stop_btn)
        
        self.translate_btn = MacButton("🚀 开始翻译", primary=True)
        self.translate_btn.setFixedSize(160, 44)
        bottom_layout.addWidget(self.translate_btn)
        
        layout.addLayout(bottom_layout)


# ==================== 主窗口 ====================

class TranslationWorkerSignals(QObject):
    """翻译工作线程信号"""
    started = pyqtSignal()
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str, str, object)


class TranslationWorker:
    """翻译工作线程"""
    
    def __init__(self, pipeline, text, options):
        self.pipeline = pipeline
        self.text = text
        self.options = options
        self.signals = TranslationWorkerSignals()
        self._stop_requested = False
    
    def request_stop(self):
        self._stop_requested = True
        self.pipeline.request_stop()
    
    def run(self):
        try:
            self.signals.started.emit()
            
            def progress_callback(stage, status, data):
                if self._stop_requested:
                    raise InterruptedError("翻译已被用户取消")
                self.signals.progress.emit(stage, status, data)
            
            result = self.pipeline.translate(self.text, self.options, progress_callback)
            
            if self._stop_requested:
                self.signals.error.emit("翻译已被用户取消")
            else:
                self.signals.finished.emit(result)
        
        except InterruptedError:
            self.signals.error.emit("翻译已被用户取消")
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            self.signals.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AI Agent Translator")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # 加载配置（优先使用 apis.json，兼容 TranslateConfig.json）
        self.config = self._load_config()
        self.agents_config = self._load_agents_config()
        self.config['agents_config'] = self.agents_config.get('agents', {})
        
        # 创建翻译流程
        self.pipeline = TranslationPipeline(self.config)
        
        # 线程池
        self.thread_pool = QThreadPool()
        
        # 当前工作线程
        self.current_worker = None
        
        # 翻译中标志
        self.is_translating = False
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """设置UI"""
        central = QWidget()
        central.setStyleSheet("background-color: #F5F5F7;")
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 左侧导航栏
        self.sidebar = MacSidebar()
        self.sidebar.nav_clicked.connect(self.on_nav_clicked)
        layout.addWidget(self.sidebar)
        
        # 右侧内容区
        self.content = QStackedWidget()
        self.content.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.content, 1)
        
        # 设置全局样式表，修复弹出控件（下拉框、弹窗）黑色背景问题
        self.setStyleSheet("""
            /* 确保弹出窗口有正确背景 */
            QWidget {
                background-color: transparent;
            }
            
            /* QComboBox 下拉列表样式 */
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #D1D1D6;
                border-radius: 8px;
                selection-background-color: #007AFF;
                selection-color: white;
                padding: 4px;
            }
            
            /* QMessageBox 弹窗样式 */
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #1D1D1F;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056CC;
            }
            
            /* QDialog 弹窗样式 */
            QDialog {
                background-color: white;
            }
            QDialog QLabel {
                color: #1D1D1F;
                background-color: transparent;
            }
            
            /* 确保下拉框本身样式正确 */
            QComboBox {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #D1D1D6;
                border-radius: 8px;
                padding: 6px 12px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #86868B;
                width: 0;
                height: 0;
            }
            QComboBox:hover {
                border-color: #007AFF;
            }
            QComboBox:focus {
                border-color: #007AFF;
            }
            
            /* SpinBox 样式 */
            QSpinBox {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #D1D1D6;
                border-radius: 6px;
                padding: 4px 8px;
            }
            
            /* CheckBox 样式 */
            QCheckBox {
                color: #1D1D1F;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #D1D1D6;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #007AFF;
                border-color: #007AFF;
            }
        """)
        
        # 初始化页面
        self.pages = {}
        
        # 快速开始页面
        self.quick_start_page = QuickStartPage()
        self.quick_start_page.nav_requested.connect(self.navigate_to)
        self.pages["quick_start"] = self.quick_start_page
        self.content.addWidget(self.quick_start_page)
        
        # 翻译页面
        self.translate_page = TranslatePage()
        self.pages["translate"] = self.translate_page
        self.content.addWidget(self.translate_page)
        
        # 接口管理页面
        self.api_manager_page = ApiManagerPage()
        self.pages["api_manager"] = self.api_manager_page
        self.content.addWidget(self.api_manager_page)
        
        # 翻译设置页面
        self.translation_settings_page = TranslationSettingsPage()
        self.pages["translation_settings"] = self.translation_settings_page
        self.content.addWidget(self.translation_settings_page)
        
        # 审核配置页面
        self.reviewer_config_page = ReviewerConfigPage()
        self.pages["reviewer_config"] = self.reviewer_config_page
        self.content.addWidget(self.reviewer_config_page)
        
        # 关于页面
        self.about_page = AboutPage()
        self.pages["about"] = self.about_page
        self.content.addWidget(self.about_page)
        
        # 占位页面
        for page_id in ["results", "glossary", "blocked_terms"]:
            page = AnimatedPage()
            layout_page = QVBoxLayout(page)
            layout_page.setContentsMargins(30, 30, 30, 30)
            
            card = MacCard()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(40, 40, 40, 40)
            
            title = QLabel(f"{page_id} - 开发中")
            title.setStyleSheet("font-size: 24px; font-weight: 600; color: #1D1D1F;")
            card_layout.addWidget(title)
            card_layout.addStretch()
            layout_page.addWidget(card)
            
            self.pages[page_id] = page
            self.content.addWidget(page)
        
        # 默认选中快速开始
        self.sidebar.set_selected("quick_start")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置（兼容新旧配置格式）
        
        优先使用 apis.json，如果不存在则创建默认配置
        """
        import os
        
        apis_file = 'config/apis.json'
        
        # 首先尝试加载新的 apis.json
        try:
            apis_config = FileUtils.read_json_file(apis_file)
            if apis_config and len(apis_config) > 0:
                # 找到第一个启用的 API 配置
                for api_id, api_info in apis_config.items():
                    if isinstance(api_info, dict) and api_info.get('enabled', True):
                        return self._convert_api_to_model_config(api_info)
                # 如果没有启用的，使用第一个
                first_api = list(apis_config.values())[0]
                if isinstance(first_api, dict):
                    return self._convert_api_to_model_config(first_api)
        except FileNotFoundError:
            logging.info("apis.json 不存在，将创建默认配置")
        except Exception as e:
            logging.warning(f"加载 apis.json 失败: {e}")
        
        # apis.json 不存在或为空，创建默认配置
        default_apis_config = {
            "siliconflow": {
                "name": "SiliconFlow",
                "icon": "⚡",
                "base_url": "https://api.siliconflow.cn/v1",
                "model": "deepseek-ai/DeepSeek-V3",
                "api_key": "",
                "enabled": True
            }
        }
        
        try:
            # 确保 config 目录存在
            os.makedirs('config', exist_ok=True)
            # 创建默认 apis.json
            with open(apis_file, 'w', encoding='utf-8') as f:
                json.dump(default_apis_config, f, ensure_ascii=False, indent=2)
            logging.info(f"已创建默认配置: {apis_file}")
            # 使用默认配置
            return self._convert_api_to_model_config(default_apis_config["siliconflow"])
        except Exception as e:
            logging.error(f"创建默认配置失败: {e}")
        
        # 回退到旧的 TranslateConfig.json（兼容旧版本）
        try:
            old_config = FileUtils.read_json_file('config/TranslateConfig.json')
            if old_config and old_config.get('model_config'):
                logging.info("使用 TranslateConfig.json 配置")
                return old_config
        except Exception:
            pass
        
        # 返回空配置
        logging.error("无法加载任何有效配置，请检查 config/apis.json 或 config/TranslateConfig.json")
        return {'model_config': {}}
    
    def _convert_api_to_model_config(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        将 apis.json 格式转换为 model_config 格式（兼容 base_agent.py）
        
        Args:
            api_info: API 配置信息
            
        Returns:
            转换后的配置字典
        """
        return {
            'model_config': {
                'base_url': api_info.get('base_url', ''),
                'model': api_info.get('model', ''),
                'api_key_list': [api_info.get('api_key', '')] if api_info.get('api_key') else []
            }
        }
    
    def _load_agents_config(self) -> Dict[str, Any]:
        """
        加载 Agent 配置（agents_config.json）
        
        如果文件不存在则创建默认配置
        
        Returns:
            Agent 配置字典
        """
        import os
        
        config_file = 'config/agents_config.json'
        
        # 尝试加载现有配置
        try:
            config = FileUtils.read_json_file(config_file)
            if config:
                return config
        except FileNotFoundError:
            logging.info(f"{config_file} 不存在，将创建默认配置")
        except Exception as e:
            logging.warning(f"加载 {config_file} 失败: {e}")
        
        # 创建默认配置
        default_config = {
            "agents": {
                "reviewer": {
                    "pass_threshold": 80,
                    "weights": {
                        "accuracy": 35,
                        "technical": 25,
                        "terminology": 20,
                        "language": 15,
                        "format": 5
                    },
                    "thresholds": {
                        "skip_optimization": 95,
                        "enter_optimization_min": 70,
                        "enter_optimization_max": 94,
                        "retranslate_max": 69
                    }
                }
            },
            "workflow": {
                "enable_iteration": True,
                "max_iterations": 3
            }
        }
        
        try:
            # 确保 config 目录存在
            os.makedirs('config', exist_ok=True)
            # 创建默认配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            logging.info(f"已创建默认配置: {config_file}")
        except Exception as e:
            logging.error(f"创建默认配置失败: {e}")
        
        return default_config
    
    def connect_signals(self):
        """连接信号"""
        tp = self.translate_page
        tp.translate_btn.clicked.connect(self.start_translation)
        tp.stop_btn.clicked.connect(self.stop_translation)
        tp.clear_src_btn.clicked.connect(self.clear_source)
        tp.clear_trans_btn.clicked.connect(self.clear_translation)
        tp.copy_btn.clicked.connect(self.copy_translation)
    
    def navigate_to(self, page_id: str):
        """导航到指定页面"""
        if page_id in self.pages:
            self.content.setCurrentWidget(self.pages[page_id])
            self.sidebar.set_selected(page_id)
    
    def on_nav_clicked(self, item_id: str):
        """导航点击处理"""
        self.navigate_to(item_id)
    
    def start_translation(self):
        """开始翻译"""
        tp = self.translate_page
        text = tp.src_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入要翻译的内容")
            return
        
        tp.trans_text.clear()
        tp.details_text.clear()
        tp.agent_panel.reset_all()
        
        tp.translate_btn.setEnabled(False)
        tp.translate_btn.setVisible(False)
        tp.stop_btn.setVisible(True)
        tp.stop_btn.setEnabled(True)
        tp.progress_bar.setVisible(True)
        tp.progress_bar.setRange(0, 0)
        
        self.is_translating = True
        
        sp = self.translation_settings_page
        options = TranslationOptions(
            target_language=sp.lang_combo.currentText(),
            temperature=sp.temp_slider.value() / 100,
            top_p=sp.topp_slider.value() / 100,
            enable_iteration=sp.iteration_check.isChecked()
        )
        
        self.current_worker = TranslationWorker(self.pipeline, text, options)
        self.current_worker.signals.started.connect(self.on_translation_started)
        self.current_worker.signals.finished.connect(self.on_translation_finished)
        self.current_worker.signals.error.connect(self.on_translation_error)
        self.current_worker.signals.progress.connect(self.on_translation_progress)
        
        self.thread_pool.start(self.current_worker.run)
    
    def on_translation_started(self):
        self.translate_page.details_text.append("🚀 翻译流程开始...")
    
    def on_translation_progress(self, stage, status, data):
        tp = self.translate_page
        
        if stage in ['source_analyzer', 'translator', 'reviewer', 'optimizer', 'reviewer2', 'reviewer_fix']:
            status_enum = AgentStatus.RUNNING if status == 'started' else \
                         AgentStatus.COMPLETED if status == 'completed' else \
                         AgentStatus.FAILED if status == 'failed' else \
                         AgentStatus.SKIPPED if status == 'skipped' else AgentStatus.PENDING
            tp.agent_panel.update_agent_status(stage, status_enum)
            
            agent_names = {
                'source_analyzer': '原语言分析专家',
                'translator': '翻译专家',
                'reviewer': '翻译审核专家',
                'optimizer': '翻译优化专家',
                'reviewer2': '优化后审核',
                'reviewer_fix': '修复审核'
            }
            
            if status == 'started':
                tp.details_text.append(f"▶️ {agent_names.get(stage, stage)}")
            elif status == 'completed':
                tp.details_text.append(f"✅ {agent_names.get(stage, stage)}")
                # 传递结果到 AgentPanel 显示简略信息
                if data and isinstance(data, dict) and 'result' in data:
                    result = data['result']
                    if result:
                        tp.agent_panel.set_agent_result(stage, result)
            elif status == 'skipped':
                tp.details_text.append(f"⏭️ {agent_names.get(stage, stage)} (跳过)")
                # 跳过状态也传递结果
                if data and isinstance(data, dict) and 'result' in data:
                    result = data['result']
                    if result:
                        result.status = AgentStatus.SKIPPED
                        tp.agent_panel.set_agent_result(stage, result)
            elif status == 'failed':
                tp.details_text.append(f"❌ {agent_names.get(stage, stage)}")
    
    def on_translation_finished(self, context):
        tp = self.translate_page
        tp.trans_text.setPlainText(context.get_final_translation())
        tp.details_text.append(f"\n📊 迭代次数: {context.iteration_count}")
        self._reset_ui()
    
    def on_translation_error(self, error_msg):
        if "取消" not in error_msg:
            QMessageBox.critical(self, "错误", f"翻译失败:\n{error_msg}")
        self.translate_page.details_text.append(f"❌ {error_msg}")
        self._reset_ui()
    
    def _reset_ui(self):
        tp = self.translate_page
        tp.translate_btn.setEnabled(True)
        tp.translate_btn.setVisible(True)
        tp.stop_btn.setVisible(False)
        tp.stop_btn.setEnabled(False)
        tp.progress_bar.setVisible(False)
        self.current_worker = None
        self.is_translating = False
    
    def stop_translation(self):
        if self.current_worker:
            self.translate_page.stop_btn.setEnabled(False)
            self.current_worker.request_stop()
    
    def clear_source(self):
        self.translate_page.src_text.clear()
        self.translate_page.trans_text.clear()
    
    def clear_translation(self):
        self.translate_page.trans_text.clear()
    
    def copy_translation(self):
        text = self.translate_page.trans_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "已复制到剪贴板")


if __name__ == "__main__":
    import sys
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setFont(QFont("-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial"))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
