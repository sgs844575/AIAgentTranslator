"""
模型模块 - 定义翻译流程中的数据模型
"""
from .agent_result import (
    AgentResult, 
    AgentStatus,
    AnalysisResult,
    TranslationResult,
    ReviewResult,
    OptimizationResult
)
from .translation_context import TranslationContext

__all__ = [
    "AgentResult",
    "AgentStatus",
    "AnalysisResult",
    "TranslationResult",
    "ReviewResult",
    "OptimizationResult",
    "TranslationContext"
]
