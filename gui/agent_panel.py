"""
Agent面板 - 显示每个Agent的工作状态和结果
"""
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QFrame, QProgressBar, QPushButton,
                             QDialog, QScrollArea, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor

from models import AgentStatus, AgentResult


class AgentDetailDialog(QDialog):
    """Agent执行详情对话框"""
    
    def __init__(self, agent_name: str, result: AgentResult, parent=None):
        super().__init__(parent)
        self.agent_name = agent_name
        self.result = result
        
        self.setWindowTitle(f"{agent_name} - 执行详情")
        self.setMinimumSize(500, 400)
        
        # 设置白色背景样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
                background-color: transparent;
            }
            QGroupBox {
                color: #333333;
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        
        info_text = f"""
        <b>Agent名称:</b> {self.agent_name}<br>
        <b>执行状态:</b> {self.result.status.value}<br>
        <b>执行次数:</b> {self.result.metadata.get('execution_count', 1)} 次<br>
        <b>执行耗时:</b> {self.result.metadata.get('execution_time', 0):.2f} 秒
        """
        
        if hasattr(self.result, 'score'):
            info_text += f"<br><b>质量评分:</b> {self.result.score}/100"
        
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.RichText)
        info_label.setWordWrap(True)
        basic_layout.addWidget(info_label)
        
        layout.addWidget(basic_group)
        
        # 输出内容
        output_group = QGroupBox("输出内容")
        output_layout = QVBoxLayout(output_group)
        
        output_text = QTextEdit()
        output_text.setReadOnly(True)
        output_text.setPlainText(self.result.output)
        output_layout.addWidget(output_text)
        
        layout.addWidget(output_group)
        
        # 详细字段（如果有）
        if self.result.details:
            details_group = QGroupBox("详细字段")
            details_layout = QVBoxLayout(details_group)
            
            details_text = QTextEdit()
            details_text.setReadOnly(True)
            
            # 格式化显示详细字段
            try:
                formatted = json.dumps(self.result.details, ensure_ascii=False, indent=2)
                details_text.setPlainText(formatted)
            except:
                details_text.setPlainText(str(self.result.details))
            
            details_layout.addWidget(details_text)
            layout.addWidget(details_group)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        layout.addStretch()


class AgentStatusCard(QFrame):
    """单个Agent状态卡片"""
    
    # 状态颜色映射
    STATUS_COLORS = {
        AgentStatus.PENDING: ("#9E9E9E", "#F5F5F5"),      # 灰色
        AgentStatus.RUNNING: ("#2196F3", "#E3F2FD"),      # 蓝色
        AgentStatus.COMPLETED: ("#4CAF50", "#E8F5E9"),    # 绿色
        AgentStatus.FAILED: ("#F44336", "#FFEBEE"),       # 红色
        AgentStatus.SKIPPED: ("#9C27B0", "#F3E5F5")       # 紫色（跳过）
    }
    
    def __init__(self, agent_name: str, agent_description: str, parent=None):
        super().__init__(parent)
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.current_status = AgentStatus.PENDING
        self.current_result = None
        
        self.setup_ui()
        self.update_status(AgentStatus.PENDING)
    
    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # 标题区域
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        self.name_label = QLabel(f"<b>{self.agent_name}</b>")
        self.name_label.setStyleSheet("font-size: 13px;")
        header_layout.addWidget(self.name_label)
        
        header_layout.addStretch()
        
        self.status_label = QLabel("等待中")
        self.status_label.setStyleSheet("font-size: 11px; color: #666;")
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # 描述
        self.desc_label = QLabel(self.agent_description)
        self.desc_label.setStyleSheet("font-size: 10px; color: #888;")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 无限进度
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(4)
        layout.addWidget(self.progress_bar)
        
        # 简略结果显示区域
        self.result_summary = QLabel("")
        self.result_summary.setStyleSheet("""
            font-size: 11px; 
            color: #3C3C43; 
            background-color: rgba(0, 122, 255, 0.08);
            border-radius: 6px;
            padding: 6px 8px;
        """)
        self.result_summary.setWordWrap(True)
        self.result_summary.setVisible(False)
        layout.addWidget(self.result_summary)
        
        # 底部区域：状态摘要 + 详情按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        # 执行统计（耗时、次数）
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 10px; color: #86868B;")
        self.stats_label.setVisible(False)
        bottom_layout.addWidget(self.stats_label)
        
        bottom_layout.addStretch()
        
        # 查看详情按钮
        self.detail_btn = QPushButton("详情")
        self.detail_btn.setFixedSize(50, 22)
        self.detail_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                background-color: #007AFF;
                color: white;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.detail_btn.setVisible(False)
        self.detail_btn.clicked.connect(self.show_details)
        bottom_layout.addWidget(self.detail_btn)
        
        layout.addLayout(bottom_layout)
    
    def update_status(self, status: AgentStatus, message: str = ""):
        """更新状态显示"""
        self.current_status = status
        
        # 获取颜色
        border_color, bg_color = self.STATUS_COLORS.get(status, ("#9E9E9E", "#F5F5F5"))
        
        # 根据状态设置边框样式
        if status == AgentStatus.SKIPPED:
            # 跳过状态使用虚线边框
            border_style = "2px dashed"
        else:
            border_style = "2px solid"
        
        # 更新样式
        self.setStyleSheet(f"""
            AgentStatusCard {{
                background-color: {bg_color};
                border: {border_style} {border_color};
                border-radius: 8px;
            }}
        """)
        
        # 更新状态标签
        status_text = {
            AgentStatus.PENDING: "等待中",
            AgentStatus.RUNNING: "执行中...",
            AgentStatus.COMPLETED: "已完成",
            AgentStatus.FAILED: "执行失败",
            AgentStatus.SKIPPED: "已跳过 ⭐"  # 添加星标表示优秀
        }.get(status, "未知")
        
        if message:
            status_text += f" - {message}"
        
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {border_color}; font-weight: bold;")
        
        # 控制进度条显示
        self.progress_bar.setVisible(status == AgentStatus.RUNNING)
    
    def _extract_summary(self, result: AgentResult) -> str:
        """从结果中提取简略信息"""
        if result.status == AgentStatus.FAILED:
            return "执行失败"
        if result.status == AgentStatus.SKIPPED:
            return "已跳过"
        
        parts = []
        
        # 根据Agent类型提取不同信息
        agent_name = result.agent_name.lower()
        details = result.details or {}
        
        if 'analyzer' in agent_name or 'analysis' in agent_name:
            # 原语言分析专家
            lang = details.get('language', '')
            complexity = details.get('complexity', '')
            if lang:
                parts.append(f"语言: {lang}")
            if complexity:
                parts.append(f"复杂度: {complexity}")
            key_terms = details.get('key_terms', [])
            if key_terms:
                terms_str = ', '.join(key_terms[:3])
                if len(key_terms) > 3:
                    terms_str += f' 等{len(key_terms)}个'
                parts.append(f"术语: {terms_str}")
                
        elif 'translator' in agent_name and 'optimizer' not in agent_name:
            # 翻译专家
            confidence = details.get('confidence', 0)
            if confidence:
                parts.append(f"置信度: {confidence:.0%}")
            notes = details.get('notes', [])
            if notes:
                parts.append(f"备注: {notes[0]}")
                
        elif 'reviewer' in agent_name or 'review' in agent_name:
            # 翻译审核专家
            score = getattr(result, 'score', 0) or details.get('score', 0)
            passed = getattr(result, 'passed', False) or details.get('passed', False)
            if score:
                status = "通过" if passed else "未通过"
                parts.append(f"评分: {score}/100 ({status})")
            issues = details.get('issues', [])
            if issues:
                parts.append(f"问题: {len(issues)}个")
            suggestions = details.get('suggestions', [])
            if suggestions:
                parts.append(f"建议: {suggestions[0][:30]}..." if len(suggestions[0]) > 30 else f"建议: {suggestions[0]}")
                
        elif 'optimizer' in agent_name:
            # 翻译优化专家
            improvements = details.get('improvements', [])
            if improvements:
                parts.append(f"改进: {len(improvements)}处")
            polish_type = details.get('polish_type', '')
            if polish_type:
                parts.append(f"类型: {polish_type}")
        
        # 如果没有提取到特定信息，使用output前50字
        if not parts and result.output:
            text = result.output.replace('\n', ' ').strip()
            if len(text) > 50:
                return f"结果: {text[:50]}..."
            else:
                return f"结果: {text}"
        
        return " | ".join(parts) if parts else "已完成"
    
    def set_result(self, result: AgentResult):
        """设置执行结果"""
        self.current_result = result
        
        # 显示简略结果
        summary = self._extract_summary(result)
        self.result_summary.setText(summary)
        self.result_summary.setVisible(True)
        
        # 执行统计
        stats_parts = []
        if result.metadata.get('execution_count', 1) > 1:
            stats_parts.append(f"执行 {result.metadata['execution_count']} 次")
        if 'execution_time' in result.metadata:
            stats_parts.append(f"耗时 {result.metadata['execution_time']:.1f}s")
        
        if stats_parts:
            self.stats_label.setText(" | ".join(stats_parts))
            self.stats_label.setVisible(True)
        
        # 显示详情按钮
        self.detail_btn.setVisible(True)
        
        self.update_status(result.status)
    
    def show_details(self):
        """显示详情对话框"""
        if self.current_result:
            dialog = AgentDetailDialog(self.agent_name, self.current_result, self)
            dialog.exec_()
    
    def reset(self):
        """重置状态"""
        self.update_status(AgentStatus.PENDING)
        self.result_summary.clear()
        self.result_summary.setVisible(False)
        self.stats_label.clear()
        self.stats_label.setVisible(False)
        self.detail_btn.setVisible(False)
        self.current_result = None


class AgentPanel(QWidget):
    """Agent面板 - 显示所有Agent的状态"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Agent信息
        # 流程：分析 → 翻译 → 审核(译后) → 优化 → 审核(优化后) → 输出
        self.agent_info = [
            ("source_analyzer", "原语言分析专家", "分析原文语言特征、复杂度和关键术语"),
            ("translator", "翻译专家", "根据分析结果进行高质量翻译"),
            ("reviewer", "翻译审核专家 (译后)", "审核翻译质量，发现问题并提出建议"),
            ("optimizer", "翻译优化专家", "对翻译进行润色和优化"),
            ("reviewer2", "翻译审核专家 (优化后)", "审核优化后的翻译质量")
        ]
        
        self.agent_cards: dict = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 创建Agent卡片（移除大标题，使用更紧凑的布局）
        for agent_key, name, desc in self.agent_info:
            card = AgentStatusCard(name, desc)
            self.agent_cards[agent_key] = card
            layout.addWidget(card)
        
        layout.addStretch(0)
    
    def update_agent_status(self, agent_key: str, status: AgentStatus, message: str = ""):
        """更新指定Agent的状态"""
        if agent_key in self.agent_cards:
            self.agent_cards[agent_key].update_status(status, message)
    
    def set_agent_result(self, agent_key: str, result: AgentResult):
        """设置Agent的执行结果"""
        if agent_key in self.agent_cards:
            self.agent_cards[agent_key].set_result(result)
    
    def reset_all(self):
        """重置所有Agent状态"""
        for card in self.agent_cards.values():
            card.reset()
    
    def highlight_current(self, agent_key: str):
        """高亮当前执行的Agent"""
        for key, card in self.agent_cards.items():
            if key == agent_key:
                card.setStyleSheet(card.styleSheet() + """
                    AgentStatusCard {
                        box-shadow: 0 0 10px rgba(33, 150, 243, 0.5);
                    }
                """)
            else:
                # 保持原有样式
                card.update_status(card.current_status)
