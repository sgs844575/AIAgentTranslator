"""
Agent结果模型 - 定义Agent执行结果的统一格式
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum


class AgentStatus(Enum):
    """Agent执行状态"""
    PENDING = "pending"           # 等待执行
    RUNNING = "running"           # 执行中
    COMPLETED = "completed"       # 完成
    FAILED = "failed"             # 失败
    SKIPPED = "skipped"           # 跳过


@dataclass
class AgentResult:
    """
    Agent执行结果
    
    Attributes:
        agent_name: Agent名称
        status: 执行状态
        output: 主要输出内容
        details: 详细输出（可选）
        metadata: 元数据（执行时间、token消耗等）
        error: 错误信息（如果有）
    """
    agent_name: str
    status: AgentStatus
    output: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "output": self.output,
            "details": self.details,
            "metadata": self.metadata,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResult":
        """从字典创建实例"""
        return cls(
            agent_name=data.get("agent_name", ""),
            status=AgentStatus(data.get("status", "pending")),
            output=data.get("output", ""),
            details=data.get("details", {}),
            metadata=data.get("metadata", {}),
            error=data.get("error")
        )


@dataclass
class AnalysisResult(AgentResult):
    """原语言分析专家的结果"""
    language: str = ""                    # 检测到的语言
    complexity: str = ""                  # 复杂度级别
    key_terms: list = field(default_factory=list)      # 关键术语
    tone_style: str = ""                  # 语气风格
    cultural_notes: list = field(default_factory=list) # 文化注释


@dataclass
class TranslationResult(AgentResult):
    """翻译专家的结果"""
    translation: str = ""                 # 翻译文本
    confidence: float = 0.0               # 置信度
    alternatives: list = field(default_factory=list)   # 备选翻译
    notes: list = field(default_factory=list)          # 翻译注释


@dataclass
class ReviewResult(AgentResult):
    """翻译审核专家的结果"""
    score: float = 0.0                    # 质量评分
    issues: list = field(default_factory=list)         # 发现的问题
    passed: bool = False                  # 是否通过审核
    suggestions: list = field(default_factory=list)    # 改进建议


@dataclass
class OptimizationResult(AgentResult):
    """翻译优化专家的结果"""
    optimized_translation: str = ""       # 优化后的翻译
    improvements: list = field(default_factory=list)   # 改进点
    polish_type: str = ""                 # 润色类型
