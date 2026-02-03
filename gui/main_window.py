"""
AI Agent Translator 主窗口
"""
import sys
import logging
from typing import Any

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QTextEdit, QPushButton, QLabel, 
                             QSlider, QFrame, QSplitter, QComboBox, QCheckBox,
                             QProgressBar, QMessageBox, QGroupBox, QScrollArea,
                             QSizePolicy, QSpinBox, QTabWidget)
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

from core import TranslationPipeline, TranslationOptions
from models import TranslationContext, AgentStatus
from utils import FileUtils
from gui.agent_panel import AgentPanel
from gui.workflow_visualizer import WorkflowVisualizer

logger = logging.getLogger(__name__)


class TranslationWorkerSignals(QObject):
    """翻译工作线程信号"""
    started = pyqtSignal()
    finished = pyqtSignal(object)  # TranslationContext
    error = pyqtSignal(str)
    progress = pyqtSignal(str, str, object)  # stage, status, data


class TranslationWorker:
    """翻译工作线程（使用QRunnable）"""
    
    def __init__(self, pipeline: TranslationPipeline, text: str, options: TranslationOptions):
        self.pipeline = pipeline
        self.text = text
        self.options = options
        self.signals = TranslationWorkerSignals()
        self._stop_requested = False
    
    def request_stop(self):
        """请求停止翻译"""
        self._stop_requested = True
        self.pipeline.request_stop()
    
    def run(self):
        """执行翻译"""
        try:
            self.signals.started.emit()
            
            def progress_callback(stage: str, status: str, data: Any):
                if self._stop_requested:
                    raise InterruptedError("翻译已被用户取消")
                self.signals.progress.emit(stage, status, data)
            
            result = self.pipeline.translate(
                self.text,
                self.options,
                progress_callback
            )
            
            # 检查是否被停止
            if self._stop_requested:
                self.signals.error.emit("翻译已被用户取消")
            else:
                self.signals.finished.emit(result)
            
        except InterruptedError as e:
            logger.info(f"翻译被取消: {e}")
            self.signals.error.emit("翻译已被用户取消")
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            self.signals.error.emit(str(e))


class MainWindow(QMainWindow):
    """AI Agent Translator 主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AI Agent Translator - 智能翻译助手")
        self.setMinimumSize(1580, 850)
        self.resize(1580, 850)
        
        # 加载配置
        self.config = FileUtils.read_json_file('config/TranslateConfig.json')
        self.agents_config = FileUtils.read_json_file('config/agents_config.json')
        
        # 将agents_config注入到config中，供Agent使用
        self.config['agents_config'] = self.agents_config.get('agents', {})
        
        # 创建翻译流程
        self.pipeline = TranslationPipeline(self.config)
        
        # 线程池
        self.thread_pool = QThreadPool()
        
        # 当前工作线程
        self.current_worker = None
        
        # 翻译中标志
        self.is_translating = False
        
        # 设置UI
        self.setup_ui()
        self.setup_styles()
        
        # 连接信号
        self.connect_signals()
    
    def setup_ui(self):
        """设置UI"""
        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 左侧面板 - Agent状态
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Agent面板
        self.agent_panel = AgentPanel()
        left_layout.addWidget(self.agent_panel)
        
        main_layout.addWidget(left_panel)
        
        # 中间面板 - 输入输出
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(15)
        
        # 配置标签页
        self.config_tabs = QTabWidget()
        self.config_tabs.setMaximumHeight(200)
        
        # ===== 基础设置标签页 =====
        basic_tab = QWidget()
        basic_layout = QHBoxLayout(basic_tab)
        basic_layout.setContentsMargins(10, 10, 10, 10)
        
        # 控制面板
        control_group = QGroupBox("翻译设置")
        control_layout = QHBoxLayout(control_group)
        
        # 目标语言选择
        lang_layout = QVBoxLayout()
        lang_label = QLabel("目标语言:")
        lang_label.setStyleSheet("font-weight: bold;")
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["中文", "英语", "日语", "韩语", "法语", "德语", "西班牙语", "俄语"])
        self.lang_combo.setCurrentText("中文")
        lang_layout.addWidget(self.lang_combo)
        control_layout.addLayout(lang_layout)
        
        # 温度参数
        temp_layout = QVBoxLayout()
        temp_label = QLabel("创意程度 (Temperature):")
        temp_label.setStyleSheet("font-weight: bold;")
        temp_layout.addWidget(temp_label)
        
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(30)
        temp_layout.addWidget(self.temp_slider)
        
        self.temp_value = QLabel("0.20")
        self.temp_value.setAlignment(Qt.AlignCenter)
        temp_layout.addWidget(self.temp_value)
        control_layout.addLayout(temp_layout)
        
        # Top-p参数
        topp_layout = QVBoxLayout()
        topp_label = QLabel("多样性 (Top-p):")
        topp_label.setStyleSheet("font-weight: bold;")
        topp_layout.addWidget(topp_label)
        
        self.topp_slider = QSlider(Qt.Horizontal)
        self.topp_slider.setRange(1, 100)
        self.topp_slider.setValue(10)
        topp_layout.addWidget(self.topp_slider)
        
        self.topp_value = QLabel("0.30")
        self.topp_value.setAlignment(Qt.AlignCenter)
        topp_layout.addWidget(self.topp_value)
        control_layout.addLayout(topp_layout)
        
        # 迭代选项
        self.iteration_check = QCheckBox("启用迭代优化")
        self.iteration_check.setChecked(True)
        self.iteration_check.setToolTip("审核不通过时自动重新翻译")
        control_layout.addWidget(self.iteration_check)
        
        control_layout.addStretch()
        basic_layout.addWidget(control_group)
        
        self.config_tabs.addTab(basic_tab, "基础设置")
        
        # ===== Reviewer配置标签页 =====
        self.reviewer_config_tab = self._create_reviewer_config_tab()
        self.config_tabs.addTab(self.reviewer_config_tab, "审核配置")
        
        center_layout.addWidget(self.config_tabs)
        
        # 文本编辑区域
        text_splitter = QSplitter(Qt.Horizontal)
        
        # 原文区域
        src_frame = QFrame()
        src_frame.setFrameStyle(QFrame.StyledPanel)
        src_layout = QVBoxLayout(src_frame)
        src_layout.setContentsMargins(10, 10, 10, 10)
        
        src_header = QHBoxLayout()
        src_label = QLabel("📄 原文")
        src_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        src_header.addWidget(src_label)
        src_header.addStretch()
        
        self.clear_src_btn = QPushButton("清空")
        self.clear_src_btn.setFixedSize(60, 28)
        src_header.addWidget(self.clear_src_btn)
        
        src_layout.addLayout(src_header)
        
        self.src_text = QTextEdit()
        self.src_text.setPlaceholderText("请输入要翻译的内容...")
        self.src_text.setAcceptRichText(False)
        self.src_text.setMinimumHeight(200)
        src_layout.addWidget(self.src_text)
        
        text_splitter.addWidget(src_frame)
        
        # 译文区域
        trans_frame = QFrame()
        trans_frame.setFrameStyle(QFrame.StyledPanel)
        trans_layout = QVBoxLayout(trans_frame)
        trans_layout.setContentsMargins(10, 10, 10, 10)
        
        trans_header = QHBoxLayout()
        trans_label = QLabel("✨ 译文")
        trans_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        trans_header.addWidget(trans_label)
        trans_header.addStretch()
        
        self.copy_btn = QPushButton("复制")
        self.copy_btn.setFixedSize(60, 28)
        trans_header.addWidget(self.copy_btn)
        
        self.clear_trans_btn = QPushButton("清空")
        self.clear_trans_btn.setFixedSize(60, 28)
        trans_header.addWidget(self.clear_trans_btn)
        
        trans_layout.addLayout(trans_header)
        
        self.trans_text = QTextEdit()
        self.trans_text.setPlaceholderText("翻译结果将显示在这里...")
        self.trans_text.setReadOnly(True)
        self.trans_text.setAcceptRichText(False)
        self.trans_text.setMinimumHeight(200)
        trans_layout.addWidget(self.trans_text)
        
        text_splitter.addWidget(trans_frame)
        text_splitter.setSizes([500, 500])
        
        center_layout.addWidget(text_splitter, 1)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        center_layout.addWidget(self.progress_bar)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.translate_btn = QPushButton("🚀 开始翻译")
        self.translate_btn.setMinimumSize(150, 45)
        self.translate_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        # 停止按钮（初始隐藏）
        self.stop_btn = QPushButton("⏹ 停止翻译")
        self.stop_btn.setMinimumSize(150, 45)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #f44336;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_btn.setVisible(False)
        
        button_layout.addStretch()
        
        # 保存配置按钮
        self.save_config_btn = QPushButton("💾 保存审核配置")
        self.save_config_btn.setMinimumSize(140, 45)
        self.save_config_btn.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                background-color: #2196F3;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.save_config_btn.clicked.connect(self._save_reviewer_config)
        self.save_config_btn.setToolTip("保存审核配置后生效")
        button_layout.addWidget(self.save_config_btn)
        
        button_layout.addSpacing(20)
        
        button_layout.addWidget(self.translate_btn)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addSpacing(20)
        
        # 状态标签
        self.save_status_label = QLabel("")
        self.save_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        button_layout.addWidget(self.save_status_label)
        
        button_layout.addStretch()
        
        center_layout.addLayout(button_layout)
        
        main_layout.addWidget(center_widget, 1)
        
        # 右侧面板 - 流程可视化
        right_panel = QWidget()
        right_panel.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 流程可视化
        self.workflow_viz = WorkflowVisualizer()
        right_layout.addWidget(self.workflow_viz)
        
        # 详情面板
        details_group = QGroupBox("执行详情")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        right_layout.addWidget(details_group)
        
        main_layout.addWidget(right_panel)
    
    def setup_styles(self):
        """设置样式"""
        # 加载样式文件
        try:
            main_style = FileUtils.read_txt_file('style/main.style')
            self.setStyleSheet(main_style)
        except:
            pass
        
        # 设置字体
        font = QFont("Microsoft YaHei UI", 10)
        QApplication.setFont(font)
    
    def connect_signals(self):
        """连接信号"""
        # 参数控制
        self.temp_slider.valueChanged.connect(self.update_temp_value)
        self.topp_slider.valueChanged.connect(self.update_topp_value)
        
        # 按钮
        self.translate_btn.clicked.connect(self.start_translation)
        self.stop_btn.clicked.connect(self.stop_translation)
        self.clear_src_btn.clicked.connect(self.clear_source)
        self.clear_trans_btn.clicked.connect(self.clear_translation)
        self.copy_btn.clicked.connect(self.copy_translation)
    
    def update_temp_value(self, value):
        """更新温度显示"""
        self.temp_value.setText(f"{value / 100:.2f}")
    
    def update_topp_value(self, value):
        """更新Top-p显示"""
        self.topp_value.setText(f"{value / 100:.2f}")
    
    def _create_reviewer_config_tab(self) -> QWidget:
        """创建Reviewer配置标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 加载Reviewer配置
        reviewer_config = self.agents_config.get('agents', {}).get('reviewer', {})
        
        # 阈值设置组
        threshold_group = QGroupBox("审核阈值")
        threshold_layout = QVBoxLayout(threshold_group)
        
        # 通过阈值
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("通过分数:"))
        self.reviewer_pass_threshold = QSpinBox()
        self.reviewer_pass_threshold.setRange(60, 95)
        self.reviewer_pass_threshold.setValue(reviewer_config.get('pass_threshold', 80))
        self.reviewer_pass_threshold.setSuffix(" 分")
        self.reviewer_pass_threshold.setToolTip("达到此分数视为审核通过")
        pass_layout.addWidget(self.reviewer_pass_threshold)
        pass_layout.addStretch()
        threshold_layout.addLayout(pass_layout)
        
        layout.addWidget(threshold_group)
        
        # 权重设置组
        weights_group = QGroupBox("审核权重")
        weights_layout = QVBoxLayout(weights_group)
        
        # 各维度权重
        self.reviewer_weights = {}
        weight_items = [
            ('accuracy', '准确性', 35),
            ('technical', '技术规范', 25),
            ('terminology', '术语一致性', 20),
            ('language', '语言表达', 15),
            ('format', '格式规范', 5)
        ]
        
        weights_config = reviewer_config.get('weights', {})
        
        for key, label, default in weight_items:
            w_layout = QHBoxLayout()
            w_layout.addWidget(QLabel(f"{label}:"))
            spin = QSpinBox()
            spin.setRange(0, 50)
            spin.setValue(weights_config.get(key, default))
            spin.setSuffix(" 分")
            self.reviewer_weights[key] = spin
            w_layout.addWidget(spin)
            w_layout.addStretch()
            weights_layout.addLayout(w_layout)
        
        layout.addWidget(weights_group)
        
        # 功能开关组
        feature_group = QGroupBox("审核项目")
        feature_layout = QVBoxLayout(feature_group)
        
        self.reviewer_checks = {}
        check_items = [
            ('check_format_tags', '格式标签检查', True),
            ('check_placeholders', '占位符检查', True),
            ('check_special_chars', '特殊字符检查', True),
            ('check_terminology', '术语一致性检查', True)
        ]
        
        for key, label, default in check_items:
            check = QCheckBox(label)
            check.setChecked(reviewer_config.get(key, default))
            self.reviewer_checks[key] = check
            feature_layout.addWidget(check)
        
        layout.addWidget(feature_group)
        layout.addStretch()
        
        return tab
    
    def _save_reviewer_config(self):
        """保存Reviewer配置"""
        if self.is_translating:
            QMessageBox.warning(self, "警告", "翻译进行中，请等待翻译完成后再保存配置")
            return
        
        # 冻结页面
        self._freeze_ui(True)
        self.save_status_label.setText("正在保存...")
        self.save_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        
        try:
            # 构建新配置
            new_config = {
                'pass_threshold': self.reviewer_pass_threshold.value(),
                'warning_threshold': self.reviewer_pass_threshold.value(),
                'weights': {
                    'accuracy': self.reviewer_weights['accuracy'].value(),
                    'technical': self.reviewer_weights['technical'].value(),
                    'terminology': self.reviewer_weights['terminology'].value(),
                    'language': self.reviewer_weights['language'].value(),
                    'format': self.reviewer_weights['format'].value()
                },
                'check_format_tags': self.reviewer_checks['check_format_tags'].isChecked(),
                'check_placeholders': self.reviewer_checks['check_placeholders'].isChecked(),
                'check_special_chars': self.reviewer_checks['check_special_chars'].isChecked(),
                'check_terminology': self.reviewer_checks['check_terminology'].isChecked()
            }
            
            # 更新agents_config
            if 'reviewer' not in self.agents_config['agents']:
                self.agents_config['agents']['reviewer'] = {}
            
            self.agents_config['agents']['reviewer'].update(new_config)
            
            # 更新config中的agents_config
            self.config['agents_config'] = self.agents_config['agents']
            
            # 重新创建Pipeline以应用新配置
            self._recreate_pipeline()
            
            # 保存成功
            self.save_status_label.setText("✓ 保存成功")
            self.save_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # 3秒后清除状态提示
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.save_status_label.setText(""))
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            self.save_status_label.setText(f"✗ 保存失败: {str(e)}")
            self.save_status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        finally:
            # 解冻页面
            self._freeze_ui(False)
    
    def _recreate_pipeline(self):
        """重新创建翻译流程以应用配置变更"""
        try:
            self.pipeline = TranslationPipeline(self.config)
        except Exception as e:
            logger.error(f"重新创建Pipeline失败: {e}")
            raise
    
    def _freeze_ui(self, frozen: bool):
        """冻结/解冻整个UI页面
        
        Args:
            frozen: True=冻结, False=解冻
        """
        # 配置标签页
        self.config_tabs.setEnabled(not frozen)
        
        # 原文输入区
        self.src_text.setEnabled(not frozen)
        
        # 翻译按钮和保存按钮（保存配置时也需要禁用）
        self.translate_btn.setEnabled(not frozen)
        self.save_config_btn.setEnabled(not frozen)
        
        # 左侧面板
        self.agent_panel.setEnabled(not frozen)
        
        # 右侧面板
        self.workflow_viz.setEnabled(not frozen)
        
        # 清空按钮
        self.clear_src_btn.setEnabled(not frozen)
        self.clear_trans_btn.setEnabled(not frozen)
        self.copy_btn.setEnabled(not frozen)
        
        # 应用样式变化提示冻结状态
        if frozen:
            self.setStyleSheet(self.styleSheet() + """
                QWidget:disabled {
                    background-color: #f0f0f0;
                }
            """)
        
        # 处理事件，确保UI更新
        from PyQt5.QtCore import QCoreApplication
        QCoreApplication.processEvents()
    
    def _set_reviewer_config_enabled(self, enabled: bool):
        """设置Reviewer配置控件的启用/禁用状态 - 翻译期间调用"""
        # 配置标签页中的控件
        self.reviewer_pass_threshold.setEnabled(enabled)
        for spin in self.reviewer_weights.values():
            spin.setEnabled(enabled)
        for check in self.reviewer_checks.values():
            check.setEnabled(enabled)
        # 保存按钮
        self.save_config_btn.setEnabled(enabled)
    
    def start_translation(self):
        """开始翻译"""
        text = self.src_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "请输入要翻译的内容")
            return
        
        # 清空之前的结果
        self.trans_text.clear()
        self.details_text.clear()
        self.agent_panel.reset_all()
        self.workflow_viz.reset()
        
        # 禁用开始按钮，显示停止按钮
        self.translate_btn.setEnabled(False)
        self.translate_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度
        
        # 标记翻译中状态，禁用配置修改
        self.is_translating = True
        self._set_reviewer_config_enabled(False)
        
        # 创建选项
        options = TranslationOptions(
            target_language=self.lang_combo.currentText(),
            temperature=self.temp_slider.value() / 100,
            top_p=self.topp_slider.value() / 100,
            enable_iteration=self.iteration_check.isChecked()
        )
        
        # 创建工作线程
        self.current_worker = TranslationWorker(self.pipeline, text, options)
        
        # 连接信号
        self.current_worker.signals.started.connect(self.on_translation_started)
        self.current_worker.signals.finished.connect(self.on_translation_finished)
        self.current_worker.signals.error.connect(self.on_translation_error)
        self.current_worker.signals.progress.connect(self.on_translation_progress)
        
        # 启动
        self.thread_pool.start(self.current_worker.run)
    
    def on_translation_started(self):
        """翻译开始"""
        self.details_text.append("🚀 翻译流程开始...")
    
    def on_translation_progress(self, stage: str, status: str, data: Any):
        """翻译进度更新"""
        # 更新流程图节点状态（包括 input 和 output）
        if stage in ['input', 'source_analyzer', 'translator', 'reviewer', 'optimizer', 'reviewer2', 'output']:
            status_enum = AgentStatus.RUNNING if status == 'started' else \
                         AgentStatus.COMPLETED if status == 'completed' else \
                         AgentStatus.FAILED if status == 'failed' else AgentStatus.PENDING
            
            self.workflow_viz.update_status(stage, status_enum)
        
        # 更新Agent面板
        if stage in ['source_analyzer', 'translator', 'reviewer', 'optimizer', 'reviewer2']:
            status_enum = AgentStatus.RUNNING if status == 'started' else \
                         AgentStatus.COMPLETED if status == 'completed' else \
                         AgentStatus.FAILED if status == 'failed' else AgentStatus.PENDING
            
            self.agent_panel.update_agent_status(stage, status_enum)
            self.workflow_viz.update_status(stage, status_enum)
            
            # 设置结果
            if status == 'completed' and data and 'result' in data:
                self.agent_panel.set_agent_result(stage, data['result'])
            
            # 更新详情
            agent_names = {
                'source_analyzer': '原语言分析专家',
                'translator': '翻译专家',
                'reviewer': '翻译审核专家 (译后)',
                'optimizer': '翻译优化专家',
                'reviewer2': '翻译审核专家 (优化后)'
            }
            
            if status == 'started':
                self.details_text.append(f"▶️ {agent_names.get(stage, stage)} 开始工作...")
            elif status == 'completed':
                self.details_text.append(f"✅ {agent_names.get(stage, stage)} 完成")
            elif status == 'failed':
                self.details_text.append(f"❌ {agent_names.get(stage, stage)} 失败: {data.get('error', '')}")
        
        # 流水线事件
        if stage == 'pipeline':
            if status == 'started':
                self.details_text.append("🔄 流水线启动")
            elif status == 'completed':
                self.details_text.append("🎉 翻译流程完成")
        
        # 迭代事件
        if stage == 'iteration':
            self.details_text.append(f"🔄 开始第 {data.get('iteration', 1)} 轮迭代优化")
        
        # 流程控制事件（返回上一个专家）
        if stage == 'flow_control' and status == 'return_to_agent':
            from_agent = data.get('from', '')
            to_agent = data.get('to', '')
            reason = data.get('reason', '')
            
            agent_names = {
                'source_analyzer': '原语言分析专家',
                'translator': '翻译专家',
                'reviewer': '翻译审核专家 (译后)',
                'reviewer2': '翻译审核专家 (优化后)',
                'optimizer': '翻译优化专家'
            }
            
            from_name = agent_names.get(from_agent, from_agent)
            to_name = agent_names.get(to_agent, to_agent)
            
            self.details_text.append(f"↩️ {from_name} → {to_name}")
            self.details_text.append(f"   原因: {reason}")
            
            # 更新工作流可视化，显示返回流程
            self.workflow_viz.highlight_return_flow(from_agent, to_agent)
    
    def on_translation_finished(self, context: TranslationContext):
        """翻译完成"""
        # 显示结果
        final_translation = context.get_final_translation()
        self.trans_text.setPlainText(final_translation)
        
        # 显示统计
        self.details_text.append("\n📊 翻译统计:")
        self.details_text.append(f"  - 迭代次数: {context.iteration_count}")
        
        # 显示两个独立的审核结果
        if context.review_result and hasattr(context.review_result, 'score'):
            review1_score = context.review_result.score
            review1_passed = getattr(context.review_result, 'passed', False)
            status1 = "✅通过" if review1_passed else "❌未通过"
            self.details_text.append(f"  - 译后审核评分: {review1_score}/100 ({status1})")
        
        if context.review2_result and hasattr(context.review2_result, 'score'):
            review2_score = context.review2_result.score
            review2_passed = getattr(context.review2_result, 'passed', False)
            status2 = "✅通过" if review2_passed else "❌未通过"
            self.details_text.append(f"  - 优化后审核评分: {review2_score}/100 ({status2})")
        
        # 恢复UI
        self._reset_ui_after_translation()
    
    def on_translation_error(self, error_msg: str):
        """翻译错误"""
        # 用户取消不显示错误对话框
        if "取消" not in error_msg:
            QMessageBox.critical(self, "错误", f"翻译失败:\n{error_msg}")
        
        self.details_text.append(f"❌ {error_msg}")
        
        # 恢复UI
        self._reset_ui_after_translation()
    
    def _reset_ui_after_translation(self):
        """翻译结束后恢复UI状态"""
        self.translate_btn.setEnabled(True)
        self.translate_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.current_worker = None
        
        # 恢复配置修改权限
        self.is_translating = False
        self._set_reviewer_config_enabled(True)
    
    def stop_translation(self):
        """停止翻译"""
        if hasattr(self, 'current_worker') and self.current_worker:
            self.details_text.append("⏹ 正在停止翻译...")
            self.stop_btn.setEnabled(False)
            self.current_worker.request_stop()
    
    def clear_source(self):
        """清空原文"""
        self.src_text.clear()
        self.trans_text.clear()  # 同时清空译文
    
    def clear_translation(self):
        """清空译文"""
        self.trans_text.clear()
    
    def copy_translation(self):
        """复制译文"""
        text = self.trans_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "提示", "已复制到剪贴板")
