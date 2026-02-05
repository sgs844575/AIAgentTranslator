"""
翻译设置页面 - 现代化的翻译配置界面
"""
import json
import logging
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QScrollArea, QFrame, QMessageBox, QSpinBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from gui.widgets import ConfigCard, ModernButton, ParameterSlider

logger = logging.getLogger(__name__)


class AnimatedPage(QWidget):
    """带动画的页面基类"""
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def showEvent(self, event):
        super().showEvent(event)


class TranslationSettingsPage(AnimatedPage):
    """
    翻译设置页面（现代化版本）
    
    职责：
    - 管理翻译参数配置
    - 设置迭代优化选项
    - 保存/加载配置
    """
    
    config_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = {}
        self.load_config()
        self.setup_ui()
    
    def load_config(self):
        """加载配置（如果不存在则创建默认配置）"""
        import os
        
        config_file = 'config/agents_config.json'
        
        # 尝试加载现有配置
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return
        except FileNotFoundError:
            logger.info(f"{config_file} 不存在，将创建默认配置")
        except Exception as e:
            logger.warning(f"加载配置失败: {e}")
        
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
            logger.info(f"已创建默认配置: {config_file}")
        except Exception as e:
            logger.error(f"创建默认配置失败: {e}")
        
        self.config = default_config
    
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
        title = QLabel("⚙️ 翻译设置")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #1D1D1F;
            background-color: transparent;
        """)
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("配置翻译参数和优化选项，获得最佳翻译效果")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #86868B;
            background-color: transparent;
            margin-bottom: 8px;
        """)
        layout.addWidget(subtitle)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(24)
        
        # ========== 基础设置卡片 ==========
        basic_card = ConfigCard(
            title="基础设置",
            description="调整翻译模型的核心参数"
        )
        
        # 目标语言选择
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(16)
        
        lang_label = QLabel("🌐 目标语言")
        lang_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #1D1D1F;
            background-color: transparent;
        """)
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "中文", "英语", "日语", "韩语", 
            "法语", "德语", "西班牙语", "俄语"
        ])
        self.lang_combo.setCurrentText("中文")
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #D1D1D6;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #007AFF;
            }
        """)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        basic_card.add_layout(lang_layout)
        
        # 创意程度滑块
        self.temp_slider = ParameterSlider(
            label="🎨 创意程度 (Temperature)",
            min_value=0,
            max_value=1,
            default_value=0.3,
            decimals=2,
            description="控制翻译的创造性。值越低，翻译越保守准确；值越高，翻译越有创造性。",
            color="#FF9500"
        )
        basic_card.add_widget(self.temp_slider)
        
        # 多样性滑块
        self.topp_slider = ParameterSlider(
            label="🎲 多样性 (Top-p)",
            min_value=0.01,
            max_value=1,
            default_value=0.1,
            decimals=2,
            description="控制词汇多样性。较低的值会产生更集中的翻译。",
            color="#5856D6"
        )
        basic_card.add_widget(self.topp_slider)
        
        scroll_layout.addWidget(basic_card)
        
        # ========== 迭代优化卡片 ==========
        iter_card = ConfigCard(
            title="迭代优化",
            description="自动优化不达标的翻译结果"
        )
        
        # 启用开关
        from PyQt5.QtWidgets import QCheckBox
        
        check_layout = QHBoxLayout()
        
        self.iteration_check = QCheckBox("启用迭代优化")
        self.iteration_check.setChecked(
            self.config.get('workflow', {}).get('enable_iteration', True)
        )
        self.iteration_check.setStyleSheet("""
            QCheckBox {
                font-size: 15px;
                font-weight: 500;
                color: #1D1D1F;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid #D1D1D6;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #007AFF;
                border-color: #007AFF;
            }
        """)
        check_layout.addWidget(self.iteration_check)
        check_layout.addStretch()
        
        iter_card.add_layout(check_layout)
        
        # 最大迭代次数
        max_iter_layout = QHBoxLayout()
        max_iter_layout.setSpacing(16)
        
        max_iter_label = QLabel("最大迭代次数")
        max_iter_label.setStyleSheet("""
            font-size: 14px;
            color: #3C3C43;
            background-color: transparent;
        """)
        max_iter_layout.addWidget(max_iter_label)
        
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 10)
        self.max_iter_spin.setValue(
            self.config.get('workflow', {}).get('max_iterations', 3)
        )
        self.max_iter_spin.setStyleSheet("""
            QSpinBox {
                background-color: white;
                border: 1px solid #D1D1D6;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
                min-width: 80px;
            }
            QSpinBox:focus {
                border-color: #007AFF;
            }
        """)
        max_iter_layout.addWidget(self.max_iter_spin)
        
        # 说明文字
        iter_help = QLabel("次（当审核不通过时自动重新翻译）")
        iter_help.setStyleSheet("""
            font-size: 13px;
            color: #86868B;
            background-color: transparent;
        """)
        max_iter_layout.addWidget(iter_help)
        max_iter_layout.addStretch()
        
        iter_card.add_layout(max_iter_layout)
        
        scroll_layout.addWidget(iter_card)
        
        # ========== 操作按钮 ==========
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        
        self.save_btn = ModernButton("💾 保存设置", primary=True)
        self.save_btn.setFixedSize(160, 48)
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)
        
        scroll_layout.addWidget(btn_container)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)
    
    def save_settings(self):
        """保存设置"""
        if 'workflow' not in self.config:
            self.config['workflow'] = {}
        
        self.config['workflow'].update({
            "enable_iteration": self.iteration_check.isChecked(),
            "max_iterations": self.max_iter_spin.value(),
        })
        
        try:
            import os
            os.makedirs('config', exist_ok=True)
            with open('config/agents_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "保存成功", "翻译设置已保存")
            self.config_saved.emit()
            logger.info("翻译设置已保存")
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "保存失败", f"保存设置时出错:\n{str(e)}")
    
    def get_temperature(self) -> float:
        """获取创意程度"""
        return self.temp_slider.value()
    
    def get_top_p(self) -> float:
        """获取多样性"""
        return self.topp_slider.value()
    
    def get_target_language(self) -> str:
        """获取目标语言"""
        return self.lang_combo.currentText()
    
    def get_enable_iteration(self) -> bool:
        """获取是否启用迭代优化"""
        return self.iteration_check.isChecked()
