"""
工作流可视化 - 显示翻译流程的可视化图表
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGraphicsEllipseItem, QGraphicsRectItem, 
                             QGraphicsTextItem, QGraphicsLineItem,
                             QGraphicsPathItem, QFrame)
from PyQt5.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QLinearGradient, QPainter

from models import AgentStatus


class WorkflowNode(QGraphicsRectItem):
    """工作流节点"""
    
    # 状态颜色
    STATUS_COLORS = {
        AgentStatus.PENDING: QColor("#BDBDBD"),
        AgentStatus.RUNNING: QColor("#2196F3"),
        AgentStatus.COMPLETED: QColor("#4CAF50"),
        AgentStatus.FAILED: QColor("#F44336"),
        AgentStatus.SKIPPED: QColor("#9C27B0")  # 紫色表示跳过
    }
    
    def __init__(self, x, y, width, height, name, description):
        super().__init__(0, 0, width, height)
        
        # 设置节点位置（通过setPos而不是rect的x,y）
        self.setPos(x, y)
        
        self.name = name
        self.description = description
        self.status = AgentStatus.PENDING
        self.node_width = width
        self.node_height = height
        
        # 设置样式
        self.setPen(QPen(QColor("#666"), 2))
        self.setBrush(QBrush(QColor("#FAFAFA")))
        self.setAcceptHoverEvents(True)
        
        # 动画效果 - 用于状态过渡
        self._animation_opacity = 1.0
        
        # 计算垂直居中的起始位置
        total_height = height
        name_height = 18  # 名称大约高度
        desc_height = 14  # 描述大约高度
        spacing = 4       # 间距
        content_height = name_height + spacing + desc_height
        start_y = (total_height - content_height) / 2
        
        # 创建文本项 - 使用相对于节点左上角的局部坐标
        self.name_item = QGraphicsTextItem(self)
        self.name_item.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
        self.name_item.setDefaultTextColor(QColor("#333"))
        self.name_item.setPlainText(name)
        # 名称水平居中
        name_rect = self.name_item.boundingRect()
        name_x = (width - name_rect.width()) / 2
        self.name_item.setPos(name_x, start_y)
        
        self.desc_item = QGraphicsTextItem(self)
        self.desc_item.setFont(QFont("Microsoft YaHei", 7))
        self.desc_item.setDefaultTextColor(QColor("#666"))
        self.desc_item.setPlainText(description)
        # 描述水平居中，在名称下方
        desc_rect = self.desc_item.boundingRect()
        desc_x = (width - min(desc_rect.width(), width - 10)) / 2
        self.desc_item.setPos(desc_x, start_y + name_height + spacing)
        
        # 状态指示器 - 右上角
        self.status_circle = QGraphicsEllipseItem(width - 16, 6, 8, 8, self)
        self.status_circle.setBrush(QBrush(self.STATUS_COLORS[AgentStatus.PENDING]))
        self.status_circle.setPen(QPen(QColor("#FFF"), 1))
    
    def set_status(self, status: AgentStatus):
        """设置节点状态"""
        self.status = status
        color = self.STATUS_COLORS.get(status, QColor("#BDBDBD"))
        self.status_circle.setBrush(QBrush(color))
        
        # 更新边框颜色和样式
        if status == AgentStatus.RUNNING:
            self.setPen(QPen(color, 3))
        elif status == AgentStatus.COMPLETED:
            self.setPen(QPen(color, 2))
        elif status == AgentStatus.FAILED:
            self.setPen(QPen(color, 2))
        elif status == AgentStatus.SKIPPED:
            # 跳过状态使用虚线边框
            pen = QPen(color, 2)
            pen.setStyle(Qt.DashLine)
            self.setPen(pen)
        else:
            self.setPen(QPen(QColor("#666"), 1))
        
        # 更新描述文本以显示跳过原因
        if status == AgentStatus.SKIPPED:
            self.desc_item.setDefaultTextColor(QColor("#9C27B0"))
            self.desc_item.setPlainText(f"{self.description} (已跳过)")
        else:
            self.desc_item.setDefaultTextColor(QColor("#666"))
            self.desc_item.setPlainText(self.description)
    
    def hoverEnterEvent(self, event):
        """鼠标悬停"""
        self.setBrush(QBrush(QColor("#F0F8FF")))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标离开"""
        self.setBrush(QBrush(QColor("#FAFAFA")))
        super().hoverLeaveEvent(event)


class WorkflowEdge(QGraphicsPathItem):
    """工作流边（连接线）"""
    
    def __init__(self, start_node: WorkflowNode, end_node: WorkflowNode, is_return_path: bool = False):
        super().__init__()
        
        self.start_node = start_node
        self.end_node = end_node
        self.is_return_path = is_return_path
        
        self.setPen(QPen(QColor("#BDBDBD"), 2))
        self.update_path()
    
    def update_path(self):
        """更新路径 - 使用节点的场景坐标计算连接点"""
        # 获取节点在场景中的位置
        start_pos = self.start_node.scenePos()
        end_pos = self.end_node.scenePos()
        
        # 获取节点尺寸
        start_rect = self.start_node.rect()
        end_rect = self.end_node.rect()
        
        if self.is_return_path:
            # 返回路径：从右侧绕回（形成回环）
            start_point = QPointF(
                start_pos.x() + start_rect.right(),
                start_pos.y() + start_rect.center().y()
            )
            end_point = QPointF(
                end_pos.x() + end_rect.right(),
                end_pos.y() + end_rect.center().y()
            )
            
            # 创建弧形路径
            path = QPainterPath()
            path.moveTo(start_point)
            
            # 控制点（向右凸出）
            control_x = max(start_point.x(), end_point.x()) + 60
            path.cubicTo(
                QPointF(control_x, start_point.y()),
                QPointF(control_x, end_point.y()),
                end_point
            )
        else:
            # 正常路径：从底部中心到顶部中心
            start_point = QPointF(
                start_pos.x() + start_rect.center().x(),
                start_pos.y() + start_rect.bottom()
            )
            end_point = QPointF(
                end_pos.x() + end_rect.center().x(),
                end_pos.y() + end_rect.top()
            )
            
            # 创建曲线路径
            path = QPainterPath()
            path.moveTo(start_point)
            
            # 使用贝塞尔曲线
            control_y = (start_point.y() + end_point.y()) / 2
            path.cubicTo(
                QPointF(start_point.x(), control_y),
                QPointF(end_point.x(), control_y),
                end_point
            )
        
        self.setPath(path)
    
    def set_active(self, active: bool):
        """设置是否激活（高亮）"""
        if active:
            self.setPen(QPen(QColor("#2196F3"), 3))
        else:
            self.setPen(QPen(QColor("#BDBDBD"), 2))
    
    def set_return_mode(self, enabled: bool):
        """设置返回模式（红色虚线，表示审核不通过返回）"""
        if enabled:
            pen = QPen(QColor("#F44336"), 3)
            pen.setStyle(Qt.DashLine)
            self.setPen(pen)
        else:
            self.setPen(QPen(QColor("#BDBDBD"), 2))


class WorkflowScene(QGraphicsScene):
    """工作流场景"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.nodes = {}
        self.edges = []
        
        self.setup_workflow()
    
    def setup_workflow(self):
        """设置工作流"""
        # 节点配置 (水平居中布局)
        # 场景宽度320，节点宽度160，居中位置x = (320-160)/2 = 80
        # 新流程：输入 → 分析 → 翻译 → 审核(译后) → 优化 → 审核(优化后) → 输出
        center_x = 80  # 水平居中位置
        node_configs = [
            ("input", "输入文本", "用户输入的原文", center_x, 30),
            ("analyzer", "原语言分析", "分析原文特征", center_x, 95),
            ("translator", "翻译", "生成译文", center_x, 160),
            ("reviewer1", "审核 (译后)", "翻译质量检查", center_x, 225),
            ("optimizer", "优化", "润色提升", center_x, 290),
            ("reviewer2", "审核 (优化后)", "优化后质量检查", center_x, 355),
            ("output", "输出结果", "最终译文", center_x, 420)
        ]
        
        # 创建节点
        for key, name, desc, x, y in node_configs:
            node = WorkflowNode(x - 80, y - 30, 160, 60, name, desc)
            self.addItem(node)
            self.nodes[key] = node
        
        # 创建连接边
        # 主流程
        connections = [
            ("input", "analyzer", False),
            ("analyzer", "translator", False),
            ("translator", "reviewer1", False),
            ("reviewer1", "optimizer", False),
            ("optimizer", "reviewer2", False),
            ("reviewer2", "output", False),
            # 添加审核反馈循环（返回路径）
            # 译后审核不通过 → 返回翻译
            ("reviewer1", "translator", True),
            # 优化后审核不通过 → 返回优化
            ("reviewer2", "optimizer", True)
        ]
        
        for start_key, end_key, is_return in connections:
            if start_key in self.nodes and end_key in self.nodes:
                edge = WorkflowEdge(self.nodes[start_key], self.nodes[end_key], is_return)
                self.addItem(edge)
                self.edges.append(edge)
        
        # 设置场景大小（适配右侧面板）
        self.setSceneRect(0, 0, 300, 470)
    
    def update_node_status(self, node_key: str, status: AgentStatus):
        """更新节点状态"""
        # 将agent_key映射到流程图节点
        mapping = {
            "input": "input",
            "source_analyzer": "analyzer",
            "translator": "translator",
            "reviewer": "reviewer1",  # 译后审核
            "optimizer": "optimizer",
            "reviewer2": "reviewer2",  # 优化后审核
            "output": "output"
        }
        
        mapped_key = mapping.get(node_key, node_key)
        if mapped_key in self.nodes:
            self.nodes[mapped_key].set_status(status)
    
    def highlight_path(self, from_key: str, to_key: str):
        """高亮路径"""
        # 重置所有边
        for edge in self.edges:
            edge.set_active(False)
        
        # 激活指定路径
        mapping = {
            "source_analyzer": "analyzer",
            "translator": "translator",
            "reviewer": "reviewer",
            "optimizer": "optimizer"
        }
        
        from_mapped = mapping.get(from_key, from_key)
        to_mapped = mapping.get(to_key, to_key)
        
        for edge in self.edges:
            if (edge.start_node == self.nodes.get(from_mapped) and 
                edge.end_node == self.nodes.get(to_mapped)):
                edge.set_active(True)
    
    def highlight_return_path(self, from_key: str, to_key: str):
        """高亮返回路径（用红色虚线表示）"""
        # 直接使用节点key，因为传入的已经是流程图节点名
        for edge in self.edges:
            start_node_key = None
            end_node_key = None
            
            # 查找边的起始和结束节点key
            for key, node in self.nodes.items():
                if node == edge.start_node:
                    start_node_key = key
                if node == edge.end_node:
                    end_node_key = key
            
            if (start_node_key == from_key and end_node_key == to_key):
                edge.set_return_mode(True)
    
    def reset_all(self):
        """重置所有节点和边"""
        for node in self.nodes.values():
            node.set_status(AgentStatus.PENDING)
        for edge in self.edges:
            edge.set_active(False)
            edge.set_return_mode(False)


class WorkflowVisualizer(QFrame):
    """工作流可视化组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMinimumWidth(280)
        self.setMaximumWidth(500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title = QLabel("<h4>📊 翻译流程</h4>")
        title.setStyleSheet("color: #333; margin: 5px;")
        layout.addWidget(title)
        
        # 图形视图
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # 场景
        self.scene = WorkflowScene()
        self.view.setScene(self.scene)
        
        layout.addWidget(self.view)
        
        # 图例
        legend_layout = QHBoxLayout()
        
        legend_items = [
            ("#BDBDBD", "等待"),
            ("#2196F3", "执行中"),
            ("#4CAF50", "完成"),
            ("#F44336", "失败"),
            ("#9C27B0", "跳过")  # 添加跳过状态
        ]
        
        for color, label in legend_items:
            indicator = QLabel(f"● {label}")
            indicator.setStyleSheet(f"color: {color}; font-size: 11px;")
            legend_layout.addWidget(indicator)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # 返回路径图例
        return_legend = QLabel("<span style='color:#F44336'>---</span> 审核未通过返回路径")
        return_legend.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(return_legend)
    
    def update_status(self, agent_key: str, status: AgentStatus):
        """更新Agent状态"""
        self.scene.update_node_status(agent_key, status)
    
    def highlight_flow(self, from_stage: str, to_stage: str):
        """高亮流程"""
        self.scene.highlight_path(from_stage, to_stage)
    
    def highlight_return_flow(self, from_stage: str, to_stage: str):
        """高亮返回流程（审核不通过时返回上一个专家）"""
        # 支持返回优化专家或翻译专家
        # reviewer -> translator (译后审核不通过)
        # reviewer2 -> optimizer (优化后审核不通过)
        mapping = {
            'source_analyzer': 'analyzer',
            'translator': 'translator',
            'reviewer': 'reviewer1',  # 译后审核
            'optimizer': 'optimizer',
            'reviewer2': 'reviewer2'  # 优化后审核
        }
        
        from_mapped = mapping.get(from_stage, from_stage)
        to_mapped = mapping.get(to_stage, to_stage)
        
        # 根据目标阶段确定返回路径
        if to_stage == 'optimizer' and from_stage == 'reviewer2':
            # 优化后审核不通过，从reviewer2返回optimizer
            to_mapped = 'optimizer'
            from_mapped = 'reviewer2'
        elif to_stage == 'translator':
            # 译后审核不通过，从reviewer1返回translator
            to_mapped = 'translator'
            from_mapped = 'reviewer1'
        
        self.scene.highlight_return_path(from_mapped, to_mapped)
    
    def reset(self):
        """重置"""
        self.scene.reset_all()
