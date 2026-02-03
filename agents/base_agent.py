"""
基础Agent类 - 所有翻译专家的基类
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from models import AgentResult, AgentStatus, TranslationContext
from clinet import LLMClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    基础Agent类
    
    所有翻译专家Agent的抽象基类，定义了统一的接口和执行流程。
    """
    
    # Agent标识
    name: str = "BaseAgent"
    description: str = "基础Agent"
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Agent
        
        Args:
            config: 配置字典，包含模型配置等
        """
        self.config = config
        self.model_config = config.get('model_config', {})
        self.api_keys = self.model_config.get('api_key_list', [])
        self.base_url = self.model_config.get('base_url', '')
        self.model = self.model_config.get('model', '')
        
        # 创建LLM客户端池
        self.llm_clients = self._create_clients()
        self.current_client_idx = 0
        
        # 执行统计
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    def _create_clients(self) -> List[LLMClient.LLMClient]:
        """创建LLM客户端池"""
        clients = []
        for key in self.api_keys:
            try:
                client = LLMClient.LLMClient(
                    api_key=key,
                    base_url=self.base_url,
                    model=self.model
                )
                clients.append(client)
            except Exception as e:
                logger.warning(f"创建LLM客户端失败: {e}")
        
        if not clients:
            raise ValueError("没有可用的LLM客户端，请检查配置")
        
        return clients
    
    def _get_next_client(self) -> LLMClient.LLMClient:
        """轮询获取下一个可用客户端"""
        client = self.llm_clients[self.current_client_idx]
        self.current_client_idx = (self.current_client_idx + 1) % len(self.llm_clients)
        return client
    
    def _call_llm(self, 
                  system_prompt: str, 
                  user_content: str,
                  temperature: float = 0.3,
                  top_p: float = 0.1,
                  max_retries: int = 3) -> str:
        """
        调用LLM获取响应
        
        Args:
            system_prompt: 系统提示词
            user_content: 用户输入内容
            temperature: 温度参数
            top_p: Top-p采样
            max_retries: 最大重试次数
            
        Returns:
            LLM响应文本
        """
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content}
        ]
        
        last_error = None
        for attempt in range(max_retries):
            try:
                client = self._get_next_client()
                response = client.completions(
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p
                )
                return response
            except Exception as e:
                last_error = e
                logger.warning(f"{self.name} LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                time.sleep(1)
        
        raise Exception(f"{self.name} LLM调用失败，已重试{max_retries}次: {last_error}")
    
    @abstractmethod
    def get_system_prompt(self, context: TranslationContext) -> str:
        """
        获取系统提示词
        
        Args:
            context: 翻译上下文
            
        Returns:
            系统提示词字符串
        """
        pass
    
    @abstractmethod
    def process(self, context: TranslationContext) -> AgentResult:
        """
        执行Agent的核心逻辑
        
        Args:
            context: 翻译上下文
            
        Returns:
            Agent执行结果
        """
        pass
    
    def execute(self, context: TranslationContext) -> AgentResult:
        """
        执行Agent（包装process方法，添加通用逻辑）
        
        Args:
            context: 翻译上下文
            
        Returns:
            Agent执行结果
        """
        start_time = time.perf_counter()
        self.execution_count += 1
        
        try:
            logger.info(f"[{self.name}] 开始执行...")
            result = self.process(context)
            
            elapsed = time.perf_counter() - start_time
            self.total_execution_time += elapsed
            
            # 更新元数据
            result.metadata['execution_time'] = elapsed
            result.metadata['execution_count'] = self.execution_count
            
            logger.info(f"[{self.name}] 执行完成，耗时: {elapsed:.2f}秒")
            return result
            
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(f"[{self.name}] 执行失败: {e}")
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e),
                metadata={'execution_time': elapsed}
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Agent执行统计"""
        avg_time = (self.total_execution_time / self.execution_count 
                   if self.execution_count > 0 else 0)
        return {
            'name': self.name,
            'execution_count': self.execution_count,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': avg_time
        }
