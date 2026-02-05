"""
审核配置页面 - 现代化的审核配置界面
"""
import json
import logging
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QScrollArea, QFrame, QMessageBox, QPushButton, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from gui.widgets import ConfigCard, ScoreSlider, WeightItem, ScoreBadge

logger = logging.getLogger(__name__)


class MacButton(QPushButton):
    """macOS 风格按钮（局部定义，避免循环导入）"""
    
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self._setup_style()
    
    def _setup_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                }
                QPushButton:hover {
                    background-color: #0056CC;
                }
                QPushButton:pressed {
                    background-color: #004494;
                }
                QPushButton:disabled {
                    background-color: #B8D4F0;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F2F2F7;
                    color: #007AFF;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                }
                QPushButton:hover {
                    background-color: #E5E5EA;
                }
                QPushButton:pressed {
                    background-color: #D1D1D6;
                }
            """)


class AnimatedPage(QWidget):
    """带动画的页面基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def showEvent(self, event):
        super().showEvent(event)


class ReviewerConfigPage(AnimatedPage):
    """
    审核配置页面（现代化版本）- 实时保存，修改后需重启生效
    
    职责：
    - 管理审核评分阈值设置（跳过优化、进入优化、重新翻译）
    - 管理审核权重配置
    - 实时自动保存
    
    特性：
    - 可视化分数阈值配置
    - 带颜色指示器的权重条
    - 实时保存配置
    - 重启生效提示
    """
    
    CONFIG_FILE = 'config/agents_config.json'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = {}
        self.weight_items = {}
        self.threshold_widgets = {}
        self._is_loading = False
        self.load_config()
        self.setup_ui()
    
    def load_config(self):
        """加载配置（如果不存在则创建默认配置）"""
        import os
        
        # 尝试加载现有配置
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return
        except FileNotFoundError:
            logger.info(f"{self.CONFIG_FILE} 不存在，将创建默认配置")
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
                        "retranslate_min": 0,
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
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            logger.info(f"已创建默认配置: {self.CONFIG_FILE}")
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
        layout.setSpacing(20)
        
        # 页面标题 + 重启提示
        header_layout = QVBoxLayout()
        
        title_row = QHBoxLayout()
        title = QLabel("🔍 审核配置")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #1D1D1F;
            background-color: transparent;
        """)
        title_row.addWidget(title)
        title_row.addStretch()
        header_layout.addLayout(title_row)
        
        # 重启提示
        restart_hint = QLabel("⚠️ 修改配置后会自动保存，重启应用后生效")
        restart_hint.setStyleSheet("""
            font-size: 13px;
            color: #FF9500;
            background-color: transparent;
            margin-top: 4px;
        """)
        header_layout.addWidget(restart_hint)
        
        # 副标题说明
        subtitle = QLabel("配置审核评分标准和权重分配，影响翻译质量评估")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #86868B;
            background-color: transparent;
        """)
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(24)
        
        reviewer_config = self.config.get('agents', {}).get('reviewer', {})
        thresholds = reviewer_config.get('thresholds', {})
        
        # ========== 阈值设置卡片 ==========
        threshold_card = ConfigCard(
            title="审核阈值",
            description="设置各流程的分数阈值范围（所有区间必须连续且不重叠）"
        )
        
        # 阈值范围可视化提示
        self.range_hint = QLabel()
        self.range_hint.setStyleSheet("""
            font-size: 13px;
            color: #007AFF;
            background-color: #E5F2FF;
            padding: 10px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        """)
        threshold_card.add_widget(self.range_hint)
        
        # 跳过优化阈值
        skip_layout = QHBoxLayout()
        skip_layout.setSpacing(16)
        
        skip_label = QLabel("跳过优化分数")
        skip_label.setFixedWidth(120)
        skip_label.setStyleSheet("font-size: 14px; color: #3C3C43; font-weight: 500;")
        skip_label.setToolTip("≥此分数直接通过，无需优化")
        skip_layout.addWidget(skip_label)
        
        self.skip_spin = QSpinBox()
        self.skip_spin.setRange(85, 100)
        self.skip_spin.setValue(thresholds.get('skip_optimization', 95))
        self.skip_spin.setSuffix(" 分及以上")
        self.skip_spin.setFixedWidth(140)
        self.skip_spin.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
        """)
        self.skip_spin.valueChanged.connect(self._on_threshold_changed)
        skip_layout.addWidget(self.skip_spin)
        
        skip_desc = QLabel("达到此分数直接通过，跳过优化流程")
        skip_desc.setStyleSheet("font-size: 12px; color: #86868B;")
        skip_layout.addWidget(skip_desc)
        skip_layout.addStretch()
        threshold_card.add_layout(skip_layout)
        
        # 进入优化范围
        optimize_layout = QHBoxLayout()
        optimize_layout.setSpacing(16)
        
        optimize_label = QLabel("进入优化分数")
        optimize_label.setFixedWidth(120)
        optimize_label.setStyleSheet("font-size: 14px; color: #3C3C43; font-weight: 500;")
        optimize_label.setToolTip("在此范围内的分数进入优化流程")
        optimize_layout.addWidget(optimize_label)
        
        self.optimize_min_spin = QSpinBox()
        self.optimize_min_spin.setRange(50, 94)
        self.optimize_min_spin.setValue(thresholds.get('enter_optimization_min', 70))
        self.optimize_min_spin.setSuffix(" 分")
        self.optimize_min_spin.setFixedWidth(80)
        self.optimize_min_spin.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
        """)
        self.optimize_min_spin.valueChanged.connect(self._on_threshold_changed)
        optimize_layout.addWidget(self.optimize_min_spin)
        
        optimize_to = QLabel("至")
        optimize_to.setStyleSheet("font-size: 14px; color: #3C3C43;")
        optimize_layout.addWidget(optimize_to)
        
        self.optimize_max_spin = QSpinBox()
        self.optimize_max_spin.setRange(50, 99)
        self.optimize_max_spin.setValue(thresholds.get('enter_optimization_max', 94))
        self.optimize_max_spin.setSuffix(" 分")
        self.optimize_max_spin.setFixedWidth(80)
        self.optimize_max_spin.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
        """)
        self.optimize_max_spin.valueChanged.connect(self._on_threshold_changed)
        optimize_layout.addWidget(self.optimize_max_spin)
        
        optimize_desc = QLabel("在此范围内的分数进入优化流程")
        optimize_desc.setStyleSheet("font-size: 12px; color: #86868B;")
        optimize_layout.addWidget(optimize_desc)
        optimize_layout.addStretch()
        threshold_card.add_layout(optimize_layout)
        
        # 重新翻译范围
        retrans_layout = QHBoxLayout()
        retrans_layout.setSpacing(16)
        
        retrans_label = QLabel("重新翻译分数")
        retrans_label.setFixedWidth(120)
        retrans_label.setStyleSheet("font-size: 14px; color: #3C3C43; font-weight: 500;")
        retrans_label.setToolTip("在此范围内的分数需要重新翻译")
        retrans_layout.addWidget(retrans_label)
        
        self.retrans_min_spin = QSpinBox()
        self.retrans_min_spin.setRange(0, 0)
        self.retrans_min_spin.setValue(0)
        self.retrans_min_spin.setSuffix(" 分")
        self.retrans_min_spin.setFixedWidth(80)
        self.retrans_min_spin.setEnabled(False)
        self.retrans_min_spin.setStyleSheet("""
            QSpinBox {
                background-color: #F2F2F7;
                color: #86868B;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
        """)
        retrans_layout.addWidget(self.retrans_min_spin)
        
        retrans_to = QLabel("至")
        retrans_to.setStyleSheet("font-size: 14px; color: #3C3C43;")
        retrans_layout.addWidget(retrans_to)
        
        self.retrans_max_spin = QSpinBox()
        self.retrans_max_spin.setRange(0, 84)
        self.retrans_max_spin.setValue(thresholds.get('retranslate_max', 69))
        self.retrans_max_spin.setSuffix(" 分")
        self.retrans_max_spin.setFixedWidth(80)
        self.retrans_max_spin.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: #1D1D1F;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
        """)
        self.retrans_max_spin.valueChanged.connect(self._on_threshold_changed)
        retrans_layout.addWidget(self.retrans_max_spin)
        
        retrans_desc = QLabel("在此范围内的分数需要重新翻译")
        retrans_desc.setStyleSheet("font-size: 12px; color: #86868B;")
        retrans_layout.addWidget(retrans_desc)
        retrans_layout.addStretch()
        threshold_card.add_layout(retrans_layout)
        
        scroll_layout.addWidget(threshold_card)
        
        # ========== 权重设置卡片 ==========
        weights_card = ConfigCard(
            title="审核权重",
            description="调整各维度在总分中的占比"
        )
        
        # 权重项配置
        weight_configs = [
            ('accuracy', '准确性', 35, '翻译内容的准确程度'),
            ('technical', '技术规范', 25, '格式、标点的规范程度'),
            ('terminology', '术语一致性', 20, '专业术语翻译的准确性'),
            ('language', '语言表达', 15, '语句通顺程度'),
            ('format', '格式规范', 5, '排版、空格等格式问题'),
        ]
        
        weights_config = reviewer_config.get('weights', {})
        
        for key, label, default, desc in weight_configs:
            item_layout = QVBoxLayout()
            item_layout.setSpacing(4)
            
            # 权重项
            weight_item = WeightItem(
                weight_type=key,
                label=label,
                default_value=weights_config.get(key, default),
                max_value=100
            )
            weight_item.valueChanged.connect(self._on_weight_changed)
            item_layout.addWidget(weight_item)
            
            # 描述文字
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("""
                font-size: 11px;
                color: #86868B;
                background-color: transparent;
                padding-left: 40px;
            """)
            item_layout.addWidget(desc_label)
            
            weights_card.add_layout(item_layout)
            self.weight_items[key] = weight_item
        
        # 总权重提示
        self.total_weight_label = QLabel("总权重: 100分")
        self.total_weight_label.setAlignment(Qt.AlignRight)
        self.total_weight_label.setStyleSheet("""
            font-size: 13px;
            color: #34C759;
            font-weight: 600;
            background-color: transparent;
            margin-top: 8px;
        """)
        weights_card.add_widget(self.total_weight_label)
        
        scroll_layout.addWidget(weights_card)
        
        # ========== 恢复默认按钮 ==========
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        
        self.reset_btn = MacButton("↩️ 恢复默认", primary=False)
        self.reset_btn.setFixedSize(140, 44)
        self.reset_btn.clicked.connect(self.reset_default)
        btn_layout.addWidget(self.reset_btn)
        
        scroll_layout.addWidget(btn_container)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)
        
        # 初始化显示
        self._update_total_weight()
        self._update_range_hint()
    
    def _on_weight_changed(self, value):
        """权重变化处理 - 实时保存"""
        self._update_total_weight()
        self._save_config()
    
    def _on_threshold_changed(self, value):
        """阈值变化处理 - 实时保存"""
        if self._is_loading:
            return
        self._update_range_hint()
        self._save_config()
        self._show_restart_hint()
    
    def _update_total_weight(self):
        """更新总权重显示"""
        total = sum(item.value() for item in self.weight_items.values())
        self.total_weight_label.setText(f"总权重: {total}分")
        
        if total == 100:
            self.total_weight_label.setStyleSheet("""
                font-size: 13px;
                color: #34C759;
                font-weight: 600;
                background-color: transparent;
                margin-top: 8px;
            """)
        elif total < 100:
            self.total_weight_label.setStyleSheet("""
                font-size: 13px;
                color: #FF9500;
                font-weight: 600;
                background-color: transparent;
                margin-top: 8px;
            """)
        else:
            self.total_weight_label.setStyleSheet("""
                font-size: 13px;
                color: #FF3B30;
                font-weight: 600;
                background-color: transparent;
                margin-top: 8px;
            """)
    
    def _update_range_hint(self):
        """更新阈值范围提示"""
        skip = self.skip_spin.value()
        opt_min = self.optimize_min_spin.value()
        opt_max = self.optimize_max_spin.value()
        ret_max = self.retrans_max_spin.value()
        
        hint_text = f"流程: 0-{ret_max}分 → 重新翻译 | {opt_min}-{opt_max}分 → 优化 | ≥{skip}分 → 通过"
        self.range_hint.setText(hint_text)
    
    def _show_restart_hint(self):
        """显示重启提示"""
        from PyQt5.QtWidgets import QMessageBox
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
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056CC;
            }
        """)
        msg_box.exec_()
    
    def _save_config(self):
        """保存配置到文件"""
        if self._is_loading:
            return
        
        if 'agents' not in self.config:
            self.config['agents'] = {}
        if 'reviewer' not in self.config['agents']:
            self.config['agents']['reviewer'] = {}
        
        reviewer = self.config['agents']['reviewer']
        
        # 保存阈值配置
        reviewer['thresholds'] = {
            'skip_optimization': self.skip_spin.value(),
            'enter_optimization_min': self.optimize_min_spin.value(),
            'enter_optimization_max': self.optimize_max_spin.value(),
            'retranslate_min': 0,
            'retranslate_max': self.retrans_max_spin.value()
        }
        
        # 保存权重配置
        reviewer['weights'] = {key: item.value() for key, item in self.weight_items.items()}
        
        try:
            import os
            os.makedirs('config', exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            logger.info("审核配置已保存")
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            QMessageBox.critical(self, "保存失败", f"保存配置时出错:\n{str(e)}")
    
    def reset_default(self):
        """恢复默认配置"""
        self._is_loading = True
        
        # 默认阈值
        self.skip_spin.setValue(95)
        self.optimize_min_spin.setValue(70)
        self.optimize_max_spin.setValue(94)
        self.retrans_max_spin.setValue(69)
        
        # 默认权重
        defaults = {
            'accuracy': 35,
            'technical': 25,
            'terminology': 20,
            'language': 15,
            'format': 5
        }
        
        for key, value in defaults.items():
            if key in self.weight_items:
                self.weight_items[key].setValue(value)
        
        self._update_total_weight()
        self._update_range_hint()
        
        self._is_loading = False
        
        # 保存默认配置
        self._save_config()
        self._show_restart_hint()
        logger.info("审核配置已恢复默认")
