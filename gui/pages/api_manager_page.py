"""
接口管理页面 - 现代化的API配置界面
"""
import json
import logging
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QScrollArea, QFrame, QMessageBox, QListWidget,
    QLineEdit, QCheckBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from gui.widgets import ConfigCard, ModernButton, ModernInput, ApiListItem

logger = logging.getLogger(__name__)


class AnimatedPage(QWidget):
    """带动画的页面基类"""
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def showEvent(self, event):
        super().showEvent(event)


class ApiManagerPage(AnimatedPage):
    """
    接口管理页面（现代化版本）
    
    职责：
    - 管理API配置列表
    - 添加/编辑/删除API
    - 测试API连接
    """
    
    config_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apis = {}
        self.current_api = None
        self._api_items = {}  # 存储ApiListItem引用
        self.load_apis()
        self.setup_ui()
    
    def load_apis(self):
        """加载API配置（如果不存在则创建默认配置）"""
        import os
        
        config_file = 'config/apis.json'
        
        # 尝试加载现有配置
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.apis = json.load(f)
                return
        except FileNotFoundError:
            logger.info(f"{config_file} 不存在，将创建默认配置")
        except Exception as e:
            logger.warning(f"加载API配置失败: {e}")
        
        # 创建默认配置
        default_apis = {
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
            # 创建默认配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_apis, f, ensure_ascii=False, indent=2)
            logger.info(f"已创建默认配置: {config_file}")
        except Exception as e:
            logger.error(f"创建默认配置失败: {e}")
        
        self.apis = default_apis
    
    def save_apis(self):
        """保存API配置"""
        import os
        os.makedirs('config', exist_ok=True)
        try:
            with open('config/apis.json', 'w', encoding='utf-8') as f:
                json.dump(self.apis, f, ensure_ascii=False, indent=2)
            logger.info("API配置已保存")
        except Exception as e:
            logger.error(f"保存API配置失败: {e}")
            raise
    
    def setup_ui(self):
        """设置现代化UI"""
        # 设置 QMessageBox 样式，防止弹窗变黑
        self.setStyleSheet("""
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
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(24)
        
        # 页面标题
        header_layout = QHBoxLayout()
        
        title = QLabel("🔌 接口管理")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #1D1D1F;
            background-color: transparent;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.add_btn = ModernButton("➕ 添加API", primary=True)
        self.add_btn.setFixedSize(140, 44)
        self.add_btn.clicked.connect(self.add_api)
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)
        
        # 副标题
        subtitle = QLabel("管理您的API接口配置，支持多个API源")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #86868B;
            background-color: transparent;
            margin-bottom: 8px;
        """)
        layout.addWidget(subtitle)
        
        # 主内容区
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        
        # ========== 左侧：API列表 ==========
        list_card = ConfigCard(title="API列表")
        list_card.setFixedWidth(320)
        
        self.api_list_widget = QWidget()
        self.api_list_layout = QVBoxLayout(self.api_list_widget)
        self.api_list_layout.setContentsMargins(0, 0, 0, 0)
        self.api_list_layout.setSpacing(8)
        self.api_list_layout.addStretch()
        
        list_card.add_widget(self.api_list_widget)
        content_layout.addWidget(list_card)
        
        # ========== 右侧：API配置 ==========
        config_card = ConfigCard(
            title="API配置",
            description="编辑选中API的详细信息"
        )
        
        # API名称
        name_card = self._create_form_field("API名称", "name_input", "例如: DeepSeek")
        config_card.add_widget(name_card)
        
        # Base URL
        url_card = self._create_form_field("Base URL", "url_input", "https://api.example.com/v1")
        config_card.add_widget(url_card)
        
        # 模型
        model_card = self._create_form_field("模型名称", "model_input", "gpt-4 或 deepseek-chat")
        config_card.add_widget(model_card)
        
        # API Key
        key_card = self._create_form_field("API Key", "key_input", "sk-xxxxxxxxxxxxxxxx", password=True)
        config_card.add_widget(key_card)
        
        # 显示密码开关
        show_key_layout = QHBoxLayout()
        self.show_key_check = QCheckBox("显示 API Key")
        self.show_key_check.stateChanged.connect(self.toggle_key_visibility)
        self.show_key_check.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #3C3C43;
                background-color: transparent;
            }
        """)
        show_key_layout.addWidget(self.show_key_check)
        show_key_layout.addStretch()
        config_card.add_layout(show_key_layout)
        
        # 启用开关
        enable_layout = QHBoxLayout()
        self.enabled_check = QCheckBox("启用此API")
        self.enabled_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #1D1D1F;
                background-color: transparent;
            }
        """)
        enable_layout.addWidget(self.enabled_check)
        enable_layout.addStretch()
        config_card.add_layout(enable_layout)
        
        config_card.add_widget(QWidget())  # 占位
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.delete_btn = ModernButton("🗑️ 删除", primary=False)
        self.delete_btn.setFixedSize(100, 44)
        self.delete_btn.clicked.connect(self.delete_api)
        btn_layout.addWidget(self.delete_btn)
        
        btn_layout.addSpacing(12)
        
        self.save_btn = ModernButton("💾 保存配置", primary=True)
        self.save_btn.setFixedSize(140, 44)
        self.save_btn.clicked.connect(self.save_current_api)
        btn_layout.addWidget(self.save_btn)
        
        config_card.add_layout(btn_layout)
        
        content_layout.addWidget(config_card, 1)
        layout.addLayout(content_layout, 1)
        
        # 刷新列表
        self.refresh_api_list()
    
    def _create_form_field(self, label: str, attr_name: str, 
                          placeholder: str = "", password: bool = False) -> QWidget:
        """创建表单字段"""
        card = QWidget()
        card.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #3C3C43;
            background-color: transparent;
        """)
        layout.addWidget(label_widget)
        
        # 输入框
        if password:
            input_widget = ModernInput(placeholder, password=True)
        else:
            input_widget = ModernInput(placeholder)
        
        setattr(self, attr_name, input_widget)
        layout.addWidget(input_widget)
        
        return card
    
    def refresh_api_list(self):
        """刷新API列表"""
        # 清空现有列表
        while self.api_list_layout.count() > 1:
            item = self.api_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self._api_items.clear()
        
        # 添加API项
        for api_id, api_config in self.apis.items():
            name = api_config.get('name', api_id)
            icon = api_config.get('icon', '🔌')
            enabled = api_config.get('enabled', False)
            
            item = ApiListItem(api_id, name, icon, enabled)
            item.clicked.connect(lambda aid=api_id: self.select_api(aid))
            self.api_list_layout.insertWidget(self.api_list_layout.count() - 1, item)
            self._api_items[api_id] = item
        
        # 默认选中第一个
        if self.apis:
            first_id = list(self.apis.keys())[0]
            self.select_api(first_id)
    
    def select_api(self, api_id: str):
        """选中API"""
        # 更新选中状态
        for aid, item in self._api_items.items():
            item.setSelected(aid == api_id)
        
        self.current_api = api_id
        api_config = self.apis.get(api_id, {})
        
        # 更新输入框
        self.name_input.setText(api_config.get('name', ''))
        self.url_input.setText(api_config.get('base_url', ''))
        self.model_input.setText(api_config.get('model', ''))
        self.key_input.setText(api_config.get('api_key', ''))
        self.enabled_check.setChecked(api_config.get('enabled', False))
    
    def toggle_key_visibility(self, state):
        """切换API Key可见性"""
        self.key_input.setPasswordMode(state != Qt.Checked)
    
    def add_api(self):
        """添加新API"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加API")
        dialog.setMinimumWidth(450)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #1D1D1F;
                font-size: 14px;
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 表单字段
        name_input = ModernInput("API名称")
        layout.addWidget(QLabel("名称:"))
        layout.addWidget(name_input)
        
        url_input = ModernInput("https://api.example.com/v1")
        layout.addWidget(QLabel("Base URL:"))
        layout.addWidget(url_input)
        
        model_input = ModernInput("模型名称")
        layout.addWidget(QLabel("模型:"))
        layout.addWidget(model_input)
        
        key_input = ModernInput("API密钥", password=True)
        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(key_input)
        
        # 按钮
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        if dialog.exec_() == QDialog.Accepted and name_input.text():
            api_id = name_input.text().lower().replace(" ", "_")
            if api_id not in self.apis:
                self.apis[api_id] = {
                    "name": name_input.text(),
                    "base_url": url_input.text(),
                    "model": model_input.text(),
                    "api_key": key_input.text(),
                    "enabled": False
                }
                self.save_apis()
                self.refresh_api_list()
                self.config_changed.emit()
    
    def save_current_api(self):
        """保存当前API配置"""
        if not self.current_api:
            QMessageBox.warning(self, "提示", "请先选择一个API")
            return
        
        self.apis[self.current_api].update({
            "name": self.name_input.text(),
            "base_url": self.url_input.text(),
            "model": self.model_input.text(),
            "api_key": self.key_input.text(),
            "enabled": self.enabled_check.isChecked()
        })
        
        try:
            self.save_apis()
            self.refresh_api_list()
            QMessageBox.information(self, "保存成功", "API配置已保存")
            self.config_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))
    
    def delete_api(self):
        """删除当前API"""
        if not self.current_api:
            return
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除API '{self.current_api}' 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.apis[self.current_api]
            self.save_apis()
            self.refresh_api_list()
            self.config_changed.emit()
