"""
翻译流程管理 - 提供高级翻译接口
"""
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from core.agent_orchestrator import AgentOrchestrator
from models import TranslationContext, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class TranslationOptions:
    """翻译选项"""
    target_language: str = "中文"
    source_language: Optional[str] = None
    domain: str = "general"
    style_preference: str = "natural"
    temperature: float = 0.3
    top_p: float = 0.1
    enable_iteration: bool = True
    max_iterations: int = 3
    skip_analysis: bool = False
    skip_review: bool = False
    skip_optimization: bool = False


class TranslationPipeline:
    """
    翻译流程管理器
    
    提供简洁的高级接口，封装复杂的Agent协作流程。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化翻译流程
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.orchestrator = AgentOrchestrator(config)
        
        # 执行历史
        self.history: list = []
        
        # 停止标志
        self._stop_requested = False
    
    def translate(self, 
                  text: str, 
                  options: Optional[TranslationOptions] = None,
                  progress_callback: Optional[Callable[[str, str, Any], None]] = None
                 ) -> TranslationContext:
        """
        执行翻译
        
        Args:
            text: 原文
            options: 翻译选项
            progress_callback: 进度回调函数
            
        Returns:
            翻译上下文（包含完整结果）
        """
        if not text or not text.strip():
            raise ValueError("原文不能为空")
        
        # 使用默认选项
        if options is None:
            options = TranslationOptions()
        
        # 创建翻译上下文
        context = TranslationContext(
            source_text=text,
            target_language=options.target_language,
            source_language=options.source_language,
            domain=options.domain,
            style_preference=options.style_preference,
            temperature=options.temperature,
            top_p=options.top_p,
            max_iterations=options.max_iterations
        )
        
        # 注册回调（先清空旧回调，防止重复注册）
        self.orchestrator.clear_progress_callbacks()
        if progress_callback:
            self.orchestrator.register_progress_callback(progress_callback)
        
        # 根据选项调整Agent
        self._configure_agents(options)
        
        try:
            # 执行翻译流程
            if options.enable_iteration:
                result_context = self.orchestrator.execute_iterative(context)
            else:
                result_context = self.orchestrator.execute_pipeline(context)
            
            # 保存历史
            self.history.append(result_context.to_dict())
            
            return result_context
            
        except Exception as e:
            logger.error(f"翻译流程执行失败: {e}")
            context.update_stage('error')
            raise
    
    def _configure_agents(self, options: TranslationOptions):
        """根据选项配置Agent"""
        # 可以在这里动态调整Agent配置
        # 例如禁用某些Agent
        pass
    
    def translate_simple(self, text: str, target_language: str = "中文") -> str:
        """
        简化翻译接口，只返回翻译结果
        
        Args:
            text: 原文
            target_language: 目标语言
            
        Returns:
            译文
        """
        options = TranslationOptions(
            target_language=target_language,
            enable_iteration=False,
            skip_optimization=True
        )
        
        context = self.translate(text, options)
        return context.get_final_translation()
    
    def get_history(self) -> list:
        """获取翻译历史"""
        return self.history
    
    def clear_history(self):
        """清空历史"""
        self.history.clear()
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """获取Agent状态"""
        return self.orchestrator.get_agent_status()
    
    def reset(self):
        """重置流程"""
        self.orchestrator.reset()
        self.clear_history()
        self._stop_requested = False
    
    def request_stop(self):
        """请求停止翻译"""
        self._stop_requested = True
        self.orchestrator.request_stop()
