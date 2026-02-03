"""
翻译上下文模型 - 管理整个翻译流程的状态和数据
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from .agent_result import AgentResult, AgentStatus


@dataclass
class TranslationContext:
    """
    翻译上下文 - 维护整个翻译流程的状态
    
    Attributes:
        source_text: 原文
        target_language: 目标语言
        source_language: 源语言（自动检测或用户指定）
        domain: 专业领域
        style_preference: 风格偏好
        history: 历史记录
        agent_results: 各Agent的执行结果
        final_output: 最终输出
        created_at: 创建时间
        completed_at: 完成时间
    """
    # 输入参数
    source_text: str
    target_language: str = "中文"
    source_language: Optional[str] = None
    domain: str = "general"
    style_preference: str = "natural"
    
    # 流程控制
    temperature: float = 0.3
    top_p: float = 0.1
    max_iterations: int = 3
    
    # 状态跟踪
    current_stage: str = "init"           # 当前阶段
    iteration_count: int = 0              # 迭代次数
    
    # 结果存储
    analysis_result: Optional[AgentResult] = None
    translation_result: Optional[AgentResult] = None
    review_result: Optional[AgentResult] = None       # 译后审核结果
    optimization_result: Optional[AgentResult] = None
    review2_result: Optional[AgentResult] = None      # 优化后审核结果（新增，独立存储）
    
    # 历史记录
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def get_final_translation(self) -> str:
        """获取最终翻译结果"""
        if self.optimization_result and self.optimization_result.output:
            return self.optimization_result.output
        elif self.translation_result and self.translation_result.output:
            return self.translation_result.output
        return ""
    
    def get_all_results(self) -> Dict[str, Optional[AgentResult]]:
        """获取所有Agent结果"""
        return {
            "analysis": self.analysis_result,
            "translation": self.translation_result,
            "review": self.review_result,
            "optimization": self.optimization_result,
            "review2": self.review2_result
        }
    
    def update_stage(self, stage: str):
        """更新当前阶段"""
        self.current_stage = stage
        self.history.append({
            "stage": stage,
            "timestamp": datetime.now().isoformat()
        })
    
    def complete(self):
        """标记翻译完成"""
        self.completed_at = datetime.now()
        self.current_stage = "completed"
    
    def needs_retranslation(self) -> bool:
        """判断是否需要重新翻译（译后审核未通过且未达最大迭代次数）"""
        if self.review_result is None:
            return False
        if self.iteration_count >= self.max_iterations:
            return False
        # 如果译后审核未通过，需要重新翻译
        if hasattr(self.review_result, 'passed'):
            return not self.review_result.passed
        return False
    
    def needs_reoptimization(self) -> bool:
        """判断是否需要重新优化（优化后审核未通过且未达最大迭代次数）"""
        if self.review2_result is None:
            return False
        if self.iteration_count >= self.max_iterations:
            return False
        # 如果优化后审核未通过，需要重新优化
        if hasattr(self.review2_result, 'passed'):
            return not self.review2_result.passed
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source_text": self.source_text,
            "target_language": self.target_language,
            "source_language": self.source_language,
            "domain": self.domain,
            "style_preference": self.style_preference,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "current_stage": self.current_stage,
            "iteration_count": self.iteration_count,
            "analysis_result": self.analysis_result.to_dict() if self.analysis_result else None,
            "translation_result": self.translation_result.to_dict() if self.translation_result else None,
            "review_result": self.review_result.to_dict() if self.review_result else None,
            "optimization_result": self.optimization_result.to_dict() if self.optimization_result else None,
            "review2_result": self.review2_result.to_dict() if self.review2_result else None,
            "final_translation": self.get_final_translation(),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
