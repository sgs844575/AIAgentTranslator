"""
设置界面 - 参考 AiNee 布局风格
左侧导航栏 + 右侧卡片式内容区
"""
import logging
from typing import Dict, Any, Callable, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QScrollArea,
    QGridLayout, QComboBox, QCheckBox, QSlider, QSpinBox,
    QGroupBox, QLineEdit, QTextEdit, QFileDialog, QMessageBox,
    QSizePolicy, QSpacerItem, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

from utils import FileUtils

logger = logging.getLogger(__name__)


class NavItem(QFrame):
    """导航项"""
    clicked = pyqtSignal(str)
    
    def __init__(self, icon: str, text: str, item_id: str, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.is_selected = False
        
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(12)
        
        # 图标
        self.icon_label = QLabel(icon)
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.icon_label)
        
        # 文字
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.text_label)
        layout.addStretch()
        
        self.setStyleSheet("""
            NavItem {
                background-color: transparent;
                border-radius: 6px;
            }
            NavItem:hover {
                background-color: #E3F2FD;
            }
            NavItem[selected="true"] {
                background-color: #1976D2;
            }
            NavItem[selected="true"] QLabel {
                color: white;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item_id)
    
    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.setProperty("selected", "true" if selected else "false")
        if selected:
            self.text_label.setStyleSheet("font-size: 13px; color: white; font-weight: bold;")
        else:
            self.text_label.setStyleSheet("font-size: 13px; color: #333333;")
        self.style().unpolish(self)
        self.style().polish(self)


class NavGroup(QFrame):
    """可折叠的导航组"""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(2)
        
        # 标题
        self.title_label = QLabel(f"  {title}")
        self.title_label.setStyleSheet("""
            font-size: 11px;
            color: #666666;
            padding: 5px 0;
        """)
        layout.addWidget(self.title_label)
        
        # 子项容器
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(2)
        layout.addWidget(self.items_widget)
        
        self.items: list[NavItem] = []
    
    def add_item(self, icon: str, text: str, item_id: str) -> NavItem:
        item = NavItem(icon, text, item_id)
        self.items_layout.addWidget(item)
        self.items.append(item)
        return item


class Sidebar(QWidget):
    """左侧导航栏"""
    nav_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet("""
            Sidebar {
                background-color: #F5F7FA;
                border-right: 1px solid #E0E6ED;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(5)
        
        # 应用标题
        title_layout = QHBoxLayout()
        title_icon = QLabel("🤖")
        title_icon.setStyleSheet("font-size: 20px;")
        title_layout.addWidget(title_icon)
        
        title_text = QLabel("AI Agent Translator")
        title_text.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #333333;
        """)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        layout.addSpacing(20)
        
        # 快速开始
        self.quick_start = NavItem("⚡", "快速开始", "quick_start")
        self.quick_start.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.quick_start)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #E0E6ED;")
        line.setFixedHeight(1)
        layout.addWidget(line)
        layout.addSpacing(10)
        
        # 接口管理组
        self.api_group = NavGroup("接口管理")
        self.api_group.add_item("🔌", "接口管理", "api_manager")
        self.api_group.add_item("▶️", "开始翻译", "translate")
        for item in self.api_group.items:
            item.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.api_group)
        
        layout.addSpacing(10)
        
        # 任务配置组
        self.task_group = NavGroup("任务配置")
        self.task_group.add_item("⚙️", "任务配置", "task_config")
        self.task_group.add_item("📝", "任务设置", "task_settings")
        self.task_group.add_item("📤", "输出设置", "output_settings")
        for item in self.task_group.items:
            item.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.task_group)
        
        layout.addSpacing(10)
        
        # 高级设置组
        self.advanced_group = NavGroup("高级设置")
        self.advanced_group.add_item("🔍", "翻译设置", "translation_settings")
        self.advanced_group.add_item("✨", "润色设置", "polish_settings")
        self.advanced_group.add_item("🧩", "插件设置", "plugin_settings")
        for item in self.advanced_group.items:
            item.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.advanced_group)
        
        layout.addSpacing(10)
        
        # 提示词管理组
        self.prompt_group = NavGroup("提示词管理")
        self.prompt_group.add_item("💬", "翻译提示词", "translation_prompt")
        self.prompt_group.add_item("🎨", "润色提示词", "polish_prompt")
        for item in self.prompt_group.items:
            item.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.prompt_group)
        
        layout.addSpacing(10)
        
        # 数据表格组
        self.data_group = NavGroup("数据表格")
        self.data_group.add_item("📚", "术语表", "glossary")
        self.data_group.add_item("🚫", "禁翻表", "blocked_terms")
        for item in self.data_group.items:
            item.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.data_group)
        
        layout.addStretch()
        
        # 底部按钮
        self.theme_btn = NavItem("🌓", "主题切换", "theme")
        self.theme_btn.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.theme_btn)
        
        self.settings_btn = NavItem("⚙️", "应用设置", "app_settings")
        self.settings_btn.clicked.connect(self._on_item_clicked)
        layout.addWidget(self.settings_btn)
        
        # 用户信息
        user_layout = QHBoxLayout()
        user_avatar = QLabel("👤")
        user_avatar.setStyleSheet("font-size: 16px;")
        user_layout.addWidget(user_avatar)
        
        user_name = QLabel("当前用户")
        user_name.setStyleSheet("font-size: 12px; color: #666666;")
        user_layout.addWidget(user_name)
        user_layout.addStretch()
        layout.addLayout(user_layout)
        
        self.current_item: Optional[NavItem] = None
    
    def _on_item_clicked(self, item_id: str):
        sender = self.sender()
        if isinstance(sender, NavItem):
            self.set_selected_item(sender)
        self.nav_clicked.emit(item_id)
    
    def set_selected_item(self, item: NavItem):
        if self.current_item:
            self.current_item.set_selected(False)
        item.set_selected(True)
        self.current_item = item


class Card(QFrame):
    """卡片组件"""
    def __init__(self, title: str, subtitle: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            Card {
                background-color: white;
                border: 1px solid #E0E6ED;
                border-radius: 8px;
            }
            Card:hover {
                border-color: #1976D2;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # 标题行
        header = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            header.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333333;
        """)
        text_layout.addWidget(title_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                font-size: 12px;
                color: #666666;
            """)
            text_layout.addWidget(subtitle_label)
        
        header.addLayout(text_layout)
        header.addStretch()
        
        layout.addLayout(header)
        
        # 内容区
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.content)
    
    def add_widget(self, widget: QWidget):
        self.content_layout.addWidget(widget)


class ApiItemWidget(QFrame):
    """API项目组件"""
    enabled_changed = pyqtSignal(str, bool)  # api_id, enabled
    delete_clicked = pyqtSignal(str)  # api_id
    
    def __init__(self, api_id: str, api_config: dict, is_first: bool = False, parent=None):
        super().__init__(parent)
        self.api_id = api_id
        self.api_config = api_config
        self.is_first = is_first
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            ApiItemWidget {
                background-color: #F5F7FA;
                border: 1px solid #E0E6ED;
                border-radius: 8px;
            }
            ApiItemWidget[enabled="true"] {
                background-color: #E3F2FD;
                border-color: #1976D2;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        # 启用复选框
        self.enable_check = QCheckBox()
        self.enable_check.setChecked(self.api_config.get("enabled", False))
        self.enable_check.stateChanged.connect(self._on_enable_changed)
        layout.addWidget(self.enable_check)
        
        # 图标和名称
        icon_label = QLabel(self.api_config.get("icon", "🔌"))
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)
        
        name_label = QLabel(self.api_config.get("name", self.api_id))
        name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
        name_label.setFixedWidth(120)
        layout.addWidget(name_label)
        
        # 模型信息
        model_text = f"{self.api_config.get('model', '未设置')}"
        model_label = QLabel(f"模型: {model_text}")
        model_label.setStyleSheet("font-size: 12px; color: #666666;")
        model_label.setFixedWidth(200)
        layout.addWidget(model_label)
        
        # Base URL
        url_text = self.api_config.get('base_url', '未设置')
        url_label = QLabel(f"地址: {url_text}")
        url_label.setStyleSheet("font-size: 12px; color: #666666;")
        url_label.setFixedWidth(250)
        layout.addWidget(url_label)
        
        layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel()
        self._update_status_label()
        layout.addWidget(self.status_label)
        
        # 删除按钮（第一个不显示）
        if not self.is_first:
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("删除此接口")
            delete_btn.setFixedSize(32, 32)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #E0E6ED;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #FFEBEE;
                    border-color: #EF5350;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.api_id))
            layout.addWidget(delete_btn)
    
    def _on_enable_changed(self, state):
        enabled = state == Qt.Checked
        self.setProperty("enabled", "true" if enabled else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._update_status_label()
        self.enabled_changed.emit(self.api_id, enabled)
    
    def _update_status_label(self):
        if self.enable_check.isChecked():
            self.status_label.setText("● 启用")
            self.status_label.setStyleSheet("font-size: 12px; color: #4CAF50; font-weight: bold;")
        else:
            self.status_label.setText("○ 未启用")
            self.status_label.setStyleSheet("font-size: 12px; color: #999999;")
    
    def set_enabled(self, enabled: bool):
        """设置启用状态（不触发信号）"""
        self.enable_check.blockSignals(True)
        self.enable_check.setChecked(enabled)
        self.enable_check.blockSignals(False)
        self.setProperty("enabled", "true" if enabled else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._update_status_label()


class AddApiDialog(QFrame):
    """添加API对话框"""
    api_added = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            AddApiDialog {
                background-color: white;
                border: 1px solid #E0E6ED;
                border-radius: 8px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #E0E6ED;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1976D2;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("添加新接口")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        layout.addWidget(title)
        
        # 表单
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # ID
        form_layout.addWidget(QLabel("ID:"), 0, 0)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("如: deepseek, openai")
        form_layout.addWidget(self.id_input, 0, 1)
        
        # 名称
        form_layout.addWidget(QLabel("名称:"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("显示名称")
        form_layout.addWidget(self.name_input, 1, 1)
        
        # 图标
        form_layout.addWidget(QLabel("图标:"), 2, 0)
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("如: 🔷, 🟢")
        form_layout.addWidget(self.icon_input, 2, 1)
        
        # Base URL
        form_layout.addWidget(QLabel("API地址:"), 3, 0)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://api.example.com/v1")
        form_layout.addWidget(self.url_input, 3, 1)
        
        # 模型
        form_layout.addWidget(QLabel("模型:"), 4, 0)
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("模型名称")
        form_layout.addWidget(self.model_input, 4, 1)
        
        # API Key
        form_layout.addWidget(QLabel("API Key:"), 5, 0)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("可选")
        form_layout.addWidget(self.key_input, 5, 1)
        
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F7FA;
                border: 1px solid #E0E6ED;
                color: #666666;
            }
            QPushButton:hover {
                background-color: #E0E6ED;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)
        
        confirm_btn = QPushButton("添加")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(confirm_btn)
        
        layout.addLayout(btn_layout)
        self.setFixedWidth(400)
    
    def _on_confirm(self):
        api_config = {
            "id": self.id_input.text().strip(),
            "name": self.name_input.text().strip() or self.id_input.text().strip(),
            "icon": self.icon_input.text().strip() or "🔌",
            "base_url": self.url_input.text().strip(),
            "model": self.model_input.text().strip(),
            "api_key": self.key_input.text().strip(),
            "enabled": False
        }
        
        if not api_config["id"]:
            return
        
        self.api_added.emit(api_config)
        self.close()


class ApiManagerPage(QWidget):
    """接口管理页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_items: dict[str, ApiItemWidget] = {}
        self.config_file = "config/apis.json"
        self.setup_ui()
        self.load_apis()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 页面标题
        title_layout = QHBoxLayout()
        title = QLabel("接口管理")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # 添加接口按钮
        add_btn = QPushButton("➕ 添加接口")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        add_btn.clicked.connect(self._show_add_dialog)
        title_layout.addWidget(add_btn)
        layout.addLayout(title_layout)
        
        # 说明
        hint = QLabel("💡 提示：同时只能启用一个接口，第一个接口（OpenAI）不可删除")
        hint.setStyleSheet("font-size: 12px; color: #666666;")
        layout.addWidget(hint)
        
        # API列表容器
        self.api_list_widget = QWidget()
        self.api_list_layout = QVBoxLayout(self.api_list_widget)
        self.api_list_layout.setContentsMargins(0, 0, 0, 0)
        self.api_list_layout.setSpacing(10)
        self.api_list_layout.addStretch()
        layout.addWidget(self.api_list_widget)
        
        layout.addStretch()
    
    def load_apis(self):
        """加载API配置"""
        try:
            apis = FileUtils.read_json(self.config_file)
            if not apis:
                apis = {}
        except:
            apis = {}
        
        # 清空现有列表
        for i in reversed(range(self.api_list_layout.count())):
            widget = self.api_list_layout.itemAt(i).widget()
            if widget and widget != self.api_list_layout.itemAt(self.api_list_layout.count() - 1).widget():
                widget.deleteLater()
        
        self.api_items.clear()
        
        # 添加API项（第一个API不显示删除按钮）
        is_first = True
        for api_id, api_config in apis.items():
            self._add_api_item(api_id, api_config, is_first)
            is_first = False
    
    def _add_api_item(self, api_id: str, api_config: dict, is_first: bool = False):
        """添加API项到列表"""
        api_item = ApiItemWidget(api_id, api_config, is_first)
        api_item.enabled_changed.connect(self._on_api_enabled_changed)
        api_item.delete_clicked.connect(self._on_api_delete)
        
        # 插入到stretch之前
        self.api_list_layout.insertWidget(self.api_list_layout.count() - 1, api_item)
        self.api_items[api_id] = api_item
    
    def _on_api_enabled_changed(self, api_id: str, enabled: bool):
        """API启用状态改变 - 互斥启用"""
        if enabled:
            # 禁用其他所有API
            for other_id, item in self.api_items.items():
                if other_id != api_id:
                    item.set_enabled(False)
        
        # 保存配置
        self._save_apis()
    
    def _on_api_delete(self, api_id: str):
        """删除API"""
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除接口 '{api_id}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从UI移除
            if api_id in self.api_items:
                self.api_items[api_id].deleteLater()
                del self.api_items[api_id]
            
            # 保存配置
            self._save_apis()
    
    def _show_add_dialog(self):
        """显示添加API对话框"""
        dialog = AddApiDialog(self)
        dialog.move(self.mapToGlobal(self.rect().center()) - dialog.rect().center())
        dialog.api_added.connect(self._on_api_added)
        dialog.show()
    
    def _on_api_added(self, api_config: dict):
        """添加新API"""
        api_id = api_config["id"]
        
        # 检查ID是否已存在
        if api_id in self.api_items:
            QMessageBox.warning(self, "添加失败", f"接口 '{api_id}' 已存在")
            return
        
        # 添加到UI
        self._add_api_item(api_id, api_config, is_first=False)
        
        # 保存配置
        self._save_apis()
    
    def _save_apis(self):
        """保存API配置到文件"""
        apis = {}
        for api_id, item in self.api_items.items():
            config = item.api_config.copy()
            config["enabled"] = item.enable_check.isChecked()
            apis[api_id] = config
        
        FileUtils.write_json(self.config_file, apis, indent=2)


class TranslationSettingsPage(QWidget):
    """翻译设置页面 - 实时保存，修改后需重启生效"""
    
    CONFIG_FILE = "config/agents_config.json"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_loading = False  # 防止加载时触发保存
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 页面标题 + 提示
        title_layout = QVBoxLayout()
        title = QLabel("翻译设置")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)
        title_layout.addWidget(title)
        
        # 重启提示
        restart_hint = QLabel("⚠️ 修改配置后需要重启应用才能生效")
        restart_hint.setStyleSheet("font-size: 12px; color: #FF9800;")
        title_layout.addWidget(restart_hint)
        layout.addLayout(title_layout)
        
        # 基础设置卡片
        basic_card = Card("⚙️", "基础设置", "")
        
        # 目标语言
        lang_layout = QHBoxLayout()
        lang_label = QLabel("目标语言:")
        lang_label.setFixedWidth(150)
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["中文", "英语", "日语", "韩语", "法语", "德语", "西班牙语", "俄语"])
        self.lang_combo.setCurrentText("中文")
        self.lang_combo.setFixedWidth(150)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        basic_card.content_layout.addLayout(lang_layout)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_label = QLabel("创意程度 (Temperature):")
        temp_label.setFixedWidth(150)
        temp_layout.addWidget(temp_label)
        
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(30)
        self.temp_slider.setFixedWidth(200)
        temp_layout.addWidget(self.temp_slider)
        
        self.temp_value = QLabel("0.30")
        self.temp_value.setFixedWidth(50)
        temp_layout.addWidget(self.temp_value)
        temp_layout.addStretch()
        basic_card.content_layout.addLayout(temp_layout)
        
        # Top-p
        topp_layout = QHBoxLayout()
        topp_label = QLabel("多样性 (Top-p):")
        topp_label.setFixedWidth(150)
        topp_layout.addWidget(topp_label)
        
        self.topp_slider = QSlider(Qt.Horizontal)
        self.topp_slider.setRange(1, 100)
        self.topp_slider.setValue(10)
        self.topp_slider.setFixedWidth(200)
        topp_layout.addWidget(self.topp_slider)
        
        self.topp_value = QLabel("0.10")
        self.topp_value.setFixedWidth(50)
        topp_layout.addWidget(self.topp_value)
        topp_layout.addStretch()
        basic_card.content_layout.addLayout(topp_layout)
        
        layout.addWidget(basic_card)
        
        # 审核配置卡片 - 分数阈值配置
        review_card = Card("🔍", "审核阈值配置", "设置各流程的分数阈值范围")
        
        # 说明文字
        hint = QLabel("分数范围: 0-100分，各区间不能重叠")
        hint.setStyleSheet("font-size: 12px; color: #666666;")
        review_card.content_layout.addWidget(hint)
        
        # 跳过优化阈值
        skip_layout = QHBoxLayout()
        skip_label = QLabel("跳过优化分数:")
        skip_label.setFixedWidth(150)
        skip_label.setToolTip("≥此分数直接通过，无需优化")
        skip_layout.addWidget(skip_label)
        
        self.skip_threshold = QSpinBox()
        self.skip_threshold.setRange(85, 100)
        self.skip_threshold.setValue(95)
        self.skip_threshold.setSuffix(" 分及以上")
        self.skip_threshold.valueChanged.connect(self._on_config_changed)
        skip_layout.addWidget(self.skip_threshold)
        skip_layout.addStretch()
        review_card.content_layout.addLayout(skip_layout)
        
        # 进入优化范围
        optimize_layout = QHBoxLayout()
        optimize_label = QLabel("进入优化分数:")
        optimize_label.setFixedWidth(150)
        optimize_label.setToolTip("在此范围内的分数进入优化流程")
        optimize_layout.addWidget(optimize_label)
        
        self.optimize_min = QSpinBox()
        self.optimize_min.setRange(50, 94)
        self.optimize_min.setValue(70)
        self.optimize_min.setSuffix(" 分")
        self.optimize_min.valueChanged.connect(self._on_config_changed)
        optimize_layout.addWidget(self.optimize_min)
        
        optimize_to = QLabel(" 至 ")
        optimize_layout.addWidget(optimize_to)
        
        self.optimize_max = QSpinBox()
        self.optimize_max.setRange(50, 99)
        self.optimize_max.setValue(94)
        self.optimize_max.setSuffix(" 分")
        self.optimize_max.valueChanged.connect(self._on_config_changed)
        optimize_layout.addWidget(self.optimize_max)
        optimize_layout.addStretch()
        review_card.content_layout.addLayout(optimize_layout)
        
        # 重新翻译范围
        retrans_layout = QHBoxLayout()
        retrans_label = QLabel("重新翻译分数:")
        retrans_label.setFixedWidth(150)
        retrans_label.setToolTip("在此范围内的分数需要重新翻译")
        retrans_layout.addWidget(retrans_label)
        
        self.retrans_min = QSpinBox()
        self.retrans_min.setRange(0, 69)
        self.retrans_min.setValue(0)
        self.retrans_min.setSuffix(" 分")
        self.retrans_min.setEnabled(False)  # 固定为0
        retrans_layout.addWidget(self.retrans_min)
        
        retrans_to = QLabel(" 至 ")
        retrans_layout.addWidget(retrans_to)
        
        self.retrans_max = QSpinBox()
        self.retrans_max.setRange(0, 69)
        self.retrans_max.setValue(69)
        self.retrans_max.setSuffix(" 分")
        self.retrans_max.valueChanged.connect(self._on_config_changed)
        retrans_layout.addWidget(self.retrans_max)
        retrans_layout.addStretch()
        review_card.content_layout.addLayout(retrans_layout)
        
        # 阈值范围可视化
        range_hint = QLabel()
        range_hint.setStyleSheet("font-size: 12px; color: #1976D2; background-color: #E3F2FD; padding: 8px; border-radius: 4px;")
        review_card.content_layout.addWidget(range_hint)
        self.range_hint = range_hint
        
        layout.addWidget(review_card)
        layout.addStretch()
        
        # 连接信号
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_value.setText(f"{v/100:.2f}")
        )
        self.topp_slider.valueChanged.connect(
            lambda v: self.topp_value.setText(f"{v/100:.2f}")
        )
        
        # 阈值联动
        self.skip_threshold.valueChanged.connect(self._update_range_hint)
        self.optimize_min.valueChanged.connect(self._update_range_hint)
        self.optimize_max.valueChanged.connect(self._update_range_hint)
        self.retrans_max.valueChanged.connect(self._update_range_hint)
    
    def load_config(self):
        """加载配置"""
        self._is_loading = True
        try:
            config = FileUtils.read_json(self.CONFIG_FILE)
            if not config:
                config = {}
            
            reviewer_config = config.get("agents", {}).get("reviewer", {})
            thresholds = reviewer_config.get("thresholds", {})
            
            # 加载阈值
            self.skip_threshold.setValue(thresholds.get("skip_optimization", 95))
            self.optimize_min.setValue(thresholds.get("enter_optimization_min", 70))
            self.optimize_max.setValue(thresholds.get("enter_optimization_max", 94))
            self.retrans_max.setValue(thresholds.get("retranslate_max", 69))
            
            self._update_range_hint()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
        finally:
            self._is_loading = False
    
    def _update_range_hint(self):
        """更新范围提示"""
        skip = self.skip_threshold.value()
        opt_min = self.optimize_min.value()
        opt_max = self.optimize_max.value()
        ret_max = self.retrans_max.value()
        
        hint_text = f"流程: 0-{ret_max}分 → 重新翻译 | {opt_min}-{opt_max}分 → 优化 | {skip}分以上 → 通过"
        self.range_hint.setText(hint_text)
    
    def _on_config_changed(self):
        """配置变更时实时保存并提示重启"""
        if self._is_loading:
            return
        
        self._save_config()
        self._show_restart_hint()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            config = FileUtils.read_json(self.CONFIG_FILE)
            if not config:
                config = {}
            
            if "agents" not in config:
                config["agents"] = {}
            if "reviewer" not in config["agents"]:
                config["agents"]["reviewer"] = {}
            
            # 更新阈值配置
            config["agents"]["reviewer"]["thresholds"] = {
                "skip_optimization": self.skip_threshold.value(),
                "enter_optimization_min": self.optimize_min.value(),
                "enter_optimization_max": self.optimize_max.value(),
                "retranslate_min": 0,
                "retranslate_max": self.retrans_max.value()
            }
            
            FileUtils.write_json(self.CONFIG_FILE, config, indent=2)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def _show_restart_hint(self):
        """显示重启提示"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("配置已更新")
        msg_box.setText("审核配置已保存，重启应用后生效")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
                background-color: transparent;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        msg_box.exec_()


class SettingsWindow(QMainWindow):
    """设置主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Agent Translator - 设置")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """设置UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 左侧导航栏
        self.sidebar = Sidebar()
        self.sidebar.nav_clicked.connect(self.on_nav_clicked)
        layout.addWidget(self.sidebar)
        
        # 右侧内容区
        self.content = QStackedWidget()
        self.content.setStyleSheet("""
            QStackedWidget {
                background-color: #FFFFFF;
            }
        """)
        layout.addWidget(self.content, 1)
        
        # 初始化页面
        self.pages: Dict[str, QWidget] = {}
        
        # 接口管理页
        self.api_manager_page = ApiManagerPage()
        self.pages["api_manager"] = self.api_manager_page
        self.content.addWidget(self.api_manager_page)
        
        # 翻译设置页
        self.translation_settings_page = TranslationSettingsPage()
        self.pages["translation_settings"] = self.translation_settings_page
        self.content.addWidget(self.translation_settings_page)
        
        # 其他页面占位
        for page_id in ["quick_start", "translate", "task_config", "task_settings",
                       "output_settings", "polish_settings", "plugin_settings",
                       "translation_prompt", "polish_prompt", "glossary", "blocked_terms",
                       "theme", "app_settings"]:
            placeholder = self._create_placeholder_page(page_id)
            self.pages[page_id] = placeholder
            self.content.addWidget(placeholder)
        
        # 默认选中接口管理
        self.sidebar.api_group.items[0].set_selected(True)
        self.sidebar.current_item = self.sidebar.api_group.items[0]
        self.content.setCurrentWidget(self.api_manager_page)
    
    def _create_placeholder_page(self, page_id: str) -> QWidget:
        """创建占位页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel(f"{page_id} - 页面开发中")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)
        layout.addWidget(title)
        
        desc = QLabel("此页面功能正在开发中，敬请期待...")
        desc.setStyleSheet("color: #666666; font-size: 14px;")
        layout.addWidget(desc)
        
        layout.addStretch()
        return page
    
    def on_nav_clicked(self, item_id: str):
        """导航点击处理"""
        if item_id in self.pages:
            self.content.setCurrentWidget(self.pages[item_id])
    
    def setup_styles(self):
        """设置全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #333333;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #E0E6ED;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #1976D2;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #E0E6ED;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                background: #1976D2;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #1976D2;
                border-radius: 3px;
            }
            QSpinBox {
                padding: 8px;
                border: 1px solid #E0E6ED;
                border-radius: 4px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        
        # 设置字体
        font = QFont("Microsoft YaHei UI", 10)
        QApplication.setFont(font)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
