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
        self.setLineWidth(2)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # 标题区域
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(f"<b>{self.agent_name}</b>")
        self.name_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(self.name_label)
        
        header_layout.addStretch()
        
        self.status_label = QLabel("等待中")
        self.status_label.setStyleSheet("font-size: 12px; color: #666;")
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # 描述
        self.desc_label = QLabel(self.agent_description)
        self.desc_label.setStyleSheet("font-size: 11px; color: #888;")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 无限进度
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 底部区域：状态摘要 + 详情按钮
        bottom_layout = QHBoxLayout()
        
        # 简洁状态显示
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 11px; color: #666;")
        self.summary_label.setVisible(False)
        bottom_layout.addWidget(self.summary_label)
        
        bottom_layout.addStretch()
        
        # 查看详情按钮
        self.detail_btn = QPushButton("查看详情")
        self.detail_btn.setFixedSize(80, 26)
        self.detail_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
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
    
    def set_result(self, result: AgentResult):
        """设置执行结果"""
        self.current_result = result
        
        # 简洁显示
        summary_parts = []
        
        if 'execution_count' in result.metadata and result.metadata['execution_count'] > 1:
            summary_parts.append(f"执行 {result.metadata['execution_count']} 次")
        
        if 'execution_time' in result.metadata:
            summary_parts.append(f"耗时 {result.metadata['execution_time']:.1f}s")
        
        if hasattr(result, 'score'):
            summary_parts.append(f"评分 {result.score}")
        
        if summary_parts:
            self.summary_label.setText(" | ".join(summary_parts))
            self.summary_label.setVisible(True)
        
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
        self.summary_label.clear()
        self.summary_label.setVisible(False)
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
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title = QLabel("<h3>🤖 AI Agent 翻译团队</h3>")
        title.setStyleSheet("color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 创建Agent卡片
        for agent_key, name, desc in self.agent_info:
            card = AgentStatusCard(name, desc)
            self.agent_cards[agent_key] = card
            layout.addWidget(card)
        
        layout.addStretch()
    
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
